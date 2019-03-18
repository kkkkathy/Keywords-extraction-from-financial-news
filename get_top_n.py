# -*- coding: utf-8 -*- 

import json, sys

def get_list(file_name):
    with open(file_name, 'r') as file:
        return set([line.strip() for line in file])

def get_top_n(n):
    global data
    area = get_list(r"/home/kathy/Desktop/text_clustering/area.txt")
    b = sorted(data, key=lambda x: data[x]["heat"], reverse=True)
    newdata = {}
    for item in b:
        if n == 0:
            break
        if item not in area:
            newdata[item] = data[item]
            print item, newdata[item]
            n -= 1
    return newdata

if __name__ == '__main__':
    #设置中文环境
    reload(sys)
    sys.setdefaultencoding("utf-8")
    with open(r"/home/kathy/Desktop/text_clustering/data.json",'r') as load_f:
        data = json.load(load_f)
    top_n = get_top_n(20)
    newdata = json.dumps(top_n, ensure_ascii=False)
    f = open(r"/home/kathy/Desktop/text_clustering/data_top20.json",'w')
    f.truncate()
    f.write(newdata)
    f.close()