# coding=utf-8  
import os  
import sys
import codecs

result = codecs.open("20160423_SinaWeibo_Num_Best.txt", 'w', 'utf-8')

num = 1

word1 = u""
word2 = u""
word3 = u""
word4 = u""
word5 = u""

flag = 1

for content in open("SinaWeibo_Info_best_1.txt",'r').readlines():
    content = unicode(content.strip('\r\n'), "utf-8")
    if "=============" in content:
        result.write(content+'\r\n')
        num = 1
    elif num <= 6:
        result.write(content+'\r\n')
    elif num == 7:
        result.write('\r\n')
    elif (u"原创微博" == content) or (u"转发微博" == content): #防止中间包含该字段
        word1 = content
        flag = 1
        #print content, flag
    elif u"点赞数:" in content:
        word2 = content
        flag += 1
        #print content, flag
    elif u"转发数: " in content:
        word3 = content
        flag += 1
        #print content, flag
    elif u"时间:" in content:
        word4 = content
        flag += 1
        #print content, flag
    elif (flag+1) == 5:
        word5 = content
        #print content
        #print flag, '\n'
    num += 1
    if u"时间: 04月23日" in word4 and word5 != "":
        #print word1
        #print word2
        #print word3
        #print word4
        #print word5
        result.write(word1+'\r\n')
        result.write(word2+'\r\n')
        result.write(word3+'\r\n')
        result.write(word4+'\r\n')
        result.write(word5+'\r\n')
        result.write('\r\n')
        word4 = u""
        word5 = u""
result.close()
