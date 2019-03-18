# -*- coding: utf-8 -*- 

import os
import sys
import codecs
import json
import jieba
import time
import jieba.posseg
import jieba.analyse
import jieba.posseg as pseg
from textrank4zh import TextRank4Keyword, TextRank4Sentence
from operator import itemgetter, attrgetter

class word:
    x = "你的" #词语本身
    w = 1.0 #tf-idf权值
    loc = 0 #位置加权
    lenth = 1.0 #词长加权
    pos = 2.0 #词性加权

    def __init__(self,x,w):
        self.x=x
        self.w=w

    def __repr__(self):
        return repr((self.x, self.w, self.loc,self.lenth,self.pos))

#去除停用词
def get_list(file_name):
    with open(file_name, 'r') as file:
        return set([line.strip() for line in file])

def is_float(aString):
    try:
        float(aString)
        return True
    except:
        return False


def label_main(fullname):
    words = []
    text = codecs.open(fullname, 'r', 'utf-8').read()
    print text
    text = text.replace("'\r\n'", "").replace("【主题】", "").replace("【正文】", "").replace(""'()'"", "").replace("\n", "").strip() #删除换行和多余的空格
    content_seg = list(jieba.cut(text, cut_all = False))
    stop_words = get_list(r"/home/kathy/Desktop/text_clustering/stop_words.txt")
    dictionary = get_list(r"/home/kathy/Desktop/text_clustering/dictionary.txt")
    entity = get_list(r"/home/kathy/Desktop/text_clustering/entities.txt")
    train_set = []
    for item in content_seg:
        if str(item) not in stop_words:  #剔除停用词
            if str(item).isdigit() == False:  #剔除数字
                if is_float(item) == False:  #剔除浮点数
                    if len(str(item).decode('utf-8')) > 1:
                        train_set.append(item)
    # for item in train_set:
    #     for d in dictionary:
    #         if d.find(str(item)) != -1:
    #             flag = 0
    #             for i in words:
    #                 if item == i.x:
    #                     flag = 1
    #             if flag == 0:
    #                 words.append(word(item, 5))
    #             break
    for item in train_set:
        for d in entity:
            if d.find(str(item)) != -1:
                flag = 0
                for i in words:
                    if item == i.x:
                        i.w += 3
                        flag = 1
                if flag == 0:
                    words.append(word(item, 20))
                break
    # maxx = 0
    # for item in words:
    #     if float(item.w) > maxx:
    #         maxx = float(item.w)
    # for item in words:
    #     item.w = int((float(item.w)/float(maxx))*10)
    return words

def label_tfidf(fullname):
    stop_words = get_list(r"/home/kathy/Desktop/text_clustering/stop_words.txt")
    f = open(fullname, "r")
    text = []
    for line in f:
        text.append(line)
    f.close()
    title = ""
    content = ""
    for i in range(len(text)):
        if i == 0:
            title = text[0].replace("【主题】", "")
        else:
            content += text[0].replace("【正文】", "")
    words = []
    jieba.analyse.set_idf_path(r"/home/kathy/Desktop/text_clustering/idf.txt.big")
    jieba.analyse.set_stop_words(r"/home/kathy/Desktop/text_clustering/stop_words.txt")
    # 将新闻标题中的tf-idf值较高的提取出来作为候选关键词,从标题中选择3个
    for x,w in jieba.analyse.extract_tags(title,topK=3, withWeight=True):
        if len(x) > 1:
            if x not in stop_words:  #剔除停用词
                if x.isdigit() == False:
                    if is_float(x) == False:  #剔除浮点数
                        words.append(word(x,w))
    #将新闻正文中的tf-idf值较高的提取出来作为候选关键词,在这个过程中处理位置加权
    for x,w in jieba.analyse.extract_tags(content,withWeight=True):
        ok = 0
        i = 0
        for i in range(0,words.__len__()):
            if words[i].x == x:
                ok = 1
                break
        if ok == 1:
            words[i].loc = 2.5
            words[i].w = w
        else:
            if len(x) > 1:
                if x not in stop_words:  #剔除停用词
                    if x.isdigit() == False:
                        if is_float(x) == False:  #剔除浮点数
                            words.append(word(x, w))
    #计算词长加权
    max_len = 0
    for i in range(0,words.__len__()):
        max_len=max(max_len,len(words[i].x))
    for i in range(0,words.__len__()):
        words[i].lenth=float(len(words[i].x))/float(max_len)
    #计算词性加权
    for i in range(0,words.__len__()):
        temp=pseg.cut(words[i].x)
        for s,flag in temp:
            if flag == 'n' :#如果为普通名词
                words[i].pos = 1.5
            elif flag[0]=='n' :#如果为专有名词
                words[i].pos = 2.0
            elif 'n' in flag :#若为包含名词的词语
                words[i].pos = 1
            else:
                words[i].pos=0
    #计算总的权值
    for i in range(0,words.__len__()):
        words[i].w += (words[i].loc+words[i].lenth+words[i].pos)
    maxx = 0
    for item in words:
        if float(item.w) > maxx:
            maxx = float(item.w)
    for item in words:
        item.w = int((float(item.w)/float(maxx))*10)
    #依照最终权值进行排序
    words=sorted(words,key=lambda WORD:WORD.w,reverse=True)
    return words


def label_textrank(fullname):
    words = []
    stop_words = get_list(r"/home/kathy/Desktop/text_clustering/stop_words.txt")
    text = codecs.open(fullname, 'r', 'utf-8').read()
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=text, lower=True, window=2)  # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象

    for item in tr4w.get_keywords(5, word_min_len=2):
        if len(item.word) > 1:
            if item.word not in stop_words:  #剔除停用词
                if item.word.isdigit() == False:
                    if is_float(item.word) == False:  #剔除浮点数
                        words.append(word(item.word, 2 + item.weight*10))
    maxx = 0
    for item in words:
        if float(item.w) > maxx:
            maxx = float(item.w)
    for item in words:
        item.w = int((float(item.w)/float(maxx))*10)
    return words

def w_compute(main_dic, tfidf, textrank):
    area = get_list(r"/home/kathy/Desktop/text_clustering/area.txt")
    wds = []
    for item in main_dic:
        wds.append(item)
    for item in tfidf:
        flag = 0
        for i in wds:
            if item.x == i.x:
                i.w += item.w
                flag = 1
                break
        if flag == 0:
            wds.append(item)
    for item in textrank:
        flag = 0
        for i in wds:
            if item.x == i.x:
                i.w += item.w
                flag = 1
                break
        if flag == 0:
            wds.append(item)
    for item in wds:
        if item.x in area:
            item.w -= 100
    wds = sorted(wds,key=lambda WORD:WORD.w,reverse=True)
    top = []
    for i in range(len(wds)):
        if i == 5:
            break
        top.append(wds[i])
        print wds[i].x, wds[i].w
    return top

def save_to_list(wds):
    global keylist
    for item in wds:
        if keylist.has_key(item.x):
            new = keylist[item.x]
            new["news"].append((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "信息抽取的内容", item.w))
            new["number"] += 1
        else:
            keylist[item.x] = {"news":[], "heat":0, "number":0}
            new = keylist[item.x]
            new["news"].append((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "信息抽取的内容", item.w))
            new["number"] += 1


if __name__ == '__main__':
    #设置中文环境
    reload(sys)
    sys.setdefaultencoding("utf-8")
    jieba.load_userdict("../dictionary.txt")
    corpus_path = r"/home/kathy/Desktop/text_clustering/news/"
    #获取每个目录下的所有文件
    catelist = os.listdir(corpus_path)
    keylist = {}
    for file_path in catelist:
        fullname = corpus_path + file_path
        main_dic = label_main(fullname)
        tfidf = label_tfidf(fullname)
        textrank = label_textrank(fullname)
        wds = w_compute(main_dic, tfidf, textrank)
        save_to_list(wds)
    data = json.dumps(keylist, ensure_ascii=False)
    f = open(r"/home/kathy/Desktop/text_clustering/data.json",'w')
    f.truncate()
    f.write(data)
    f.close()