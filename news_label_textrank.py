#-*- encoding:utf-8 -*-
from __future__ import print_function

import sys
import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence



try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

text = codecs.open(r'/home/kathy/Desktop/text_clustering/news/2', 'r', 'utf-8').read()
tr4w = TextRank4Keyword()

tr4w.analyze(text=text, lower=True, window=2)  # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象

print( '关键词：' )
for item in tr4w.get_keywords(10, word_min_len=2):
    print(item.word, item.weight * 10)

print()
print( '关键短语：' )
for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2):
    print(phrase)

tr4s = TextRank4Sentence()
tr4s.analyze(text=text, lower=True, source = 'all_filters')