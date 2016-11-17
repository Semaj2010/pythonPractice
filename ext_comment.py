#-*-coding: utf-8 -*-
# 한글
file = input("input file name : ")
f = open(file)
lines = (t.strip() for t in f)

comments = (t for t in lines if t[0] == '#')
for c in comments :
    print(c)