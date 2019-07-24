import json
import random
import logging
import pickle
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
import re
import os
import sys

from skilldatabase import skillDB

text = r" "

for filename in os.listdir('samples_txt'):
    if filename[-4:]=='.txt':
        with open('samples_txt/'+filename,'rb') as f:
            content = str(f.read())[2:]
    else:
        continue
    content_token = word_tokenize(content)

    outputCategory = {}
    sword_index = []

    for i in range(len(content_token)):
        for category, sArray in skillDB.items():
            if content_token[i] not in sArray:
                continue
            if category in outputCategory:
                if content_token[i] in outputCategory[category]:
                    sword_index.append(i)
                    continue
                outputCategory[category].append(content_token[i])
                sword_index.append(i)
            else:
                outputCategory[category] = [content_token[i]]
                sword_index.append(i)

    for key, value in outputCategory.items():
        print (key + " : " + ', '.join(value))

    json_dict = {}
    c = 1
    annot = []
    cont = ""
    for i in range(len(content_token)):
        indict = {}
        if i in sword_index:
            indict["label"]=["Skills"]
            indict["points"]=[{"start":c,"end":c+len(content_token[i]),"text":content_token[i]}]
        if len(indict)>0:
            annot.append(indict)

        cont = cont + content_token[i] + " "
        c = c + len(content_token) + 1

    json_dict["content"] = cont.replace("\'"," ").replace('\"'," ")
    json_dict["annotation"] = annot

    text = text + str(json_dict) + "\n"

text = text.replace("\'", "\"")
text = r'{0}'.format(text)
with open('test.json', 'w') as f:
    f.write(text)
