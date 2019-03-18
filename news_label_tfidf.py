# -*- coding: utf-8 -*- 

import sys
import jieba
import jieba.posseg
import jieba.analyse
import jieba.posseg as pseg
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


#新闻正文应该是包含了新闻标题的
title=u"北京去年财政收入同比增6.8% 高新技术企业贡献率达到30%"
content=u"北京市财政局日前公布2017年北京财政收入的“大账本”，全市一般公共预算收入累计完成5430.8亿元，同比增长6.8%。重点功能区支撑作用日益明显，六大高端产业功能区企业贡献了近三成的财政收入；高新技术企业对全市财政收入增长贡献率达到30%。（北京日报）"

jieba.add_word("高新技术企业")

words = []

# 将新闻标题中的tf-idf值较高的提取出来作为候选关键词,从标题中选择3个
for x,w in jieba.analyse.extract_tags(title,topK=3,withWeight=True):
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
        words[i].pos=1.5
    elif flag[0]=='n' :#如果为专有名词
        words[i].pos=2.0
    elif 'n' in flag :#若为包含名词的词语
        words[i].pos=1.0
    else:
        words[i].pos=0

#计算总的权值
for i in range(0,words.__len__()):
    words[i].w*=(1+words[i].loc+words[i].lenth+words[i].pos)

#依照最终权值进行排序
    words=sorted(words,key=lambda WORD:WORD.w,reverse=True)

#取出前五个作为标签
for i in range(0,5):
    print words[i].x, words[i].w


# if __name__ == '__main__':
#     #设置中文环境
#     reload(sys)
#     sys.setdefaultencoding("utf-8")
#     corpus_path = r"/home/kathy/Desktop/text_clustering/news/"
#     #获取每个目录下的所有文件
#     catelist = os.listdir(corpus_path)
#     for file_path in catelist:
#         fullname = corpus_path + file_path
        