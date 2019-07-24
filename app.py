import json
import random
import logging
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_fscore_support
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
import spacy
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from sklearn.metrics import accuracy_score
import pickle
import re
import sys
import os

from skilldatabase import skillDB

def trim_entity_spans(data: list) -> list:
    invalid_span_tokens = re.compile(r'\s')

    cleaned_data = []
    for text, annotations in data:
        entities = annotations['entities']
        valid_entities = []
        for start, end, label in entities:
            valid_start = start
            valid_end = end
            while valid_start < len(text) and invalid_span_tokens.match(
                    text[valid_start]):
                valid_start += 1
            while valid_end > 1 and invalid_span_tokens.match(
                    text[valid_end - 1]):
                valid_end -= 1
            valid_entities.append([valid_start, valid_end, label])
        cleaned_data.append([text, {'entities': valid_entities}])

    return cleaned_data

def convert_to_spacy(JSON_FilePath):
    try:
        training_data = []
        lines=[]
        with open(JSON_FilePath, 'rb') as f:
            lines = f.readlines()

        for line in lines:
            data = json.loads(line)
            text = data['content']
            entities = []
            for annotation in data['annotation']:
                #only a single point in text annotation.
                point = annotation['points'][0]
                labels = annotation['label']
                # handle both list of labels or a single label.
                if not isinstance(labels, list):
                    labels = [labels]

                for label in labels:
                    #indices are both inclusive [start, end] but spacy is not [start, end)
                    entities.append((point['start'], point['end'] + 1 ,label))


            training_data.append((text, {"entities" : entities}))

        return trim_entity_spans(training_data)
    except Exception as e:
        logging.exception("Unable to process " + JSON_FilePath + "\n" + "error = " + str(e))
        return None

def txt_sample_to_json(filename):
    jsn = {}
    jsn['content']=[]
    jsn['annotation']=[]
    with open(filename,'r') as f:
        jsn['content'].append(f.read())
    with open(filename[:-4]+'.json', 'w') as outfile:
        json.dump(jsn, outfile)
    return jsn

def parse_to_json(filename):

    text = r""
    if filename[-4:]=='.txt':
        with open(filename,'rb') as f:
            content = str(f.read())[2:]

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
    c = 0
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
        c = c + len(content_token)

    json_dict["content"] = cont.replace("\'"," ").replace('\"'," ")
    json_dict["annotation"] = annot

    text = text + str(json_dict) + "\n"

    text = text.replace("\'", "\"")
    text = r'{0}'.format(text)

    return text


def runapp(text):
    content_token = word_tokenize(text)

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

    word_f = {}
    for i in sword_index:
        word = content_token[i]
        if not word_f.get(word,0):
            word_f[word] = 1
        else:
            word_f[word] += 1

    return outputCategory, word_f


if __name__=="__main__":
    #load nlp
    with open('nlp.pickle','rb') as f:
        nlp = pickle.load(f)

    try:
        filename = sys.argv[1]

        if filename[-4:]=='json':
            doc_to_test = convert_to_spacy(filename)
            for text, annotation in doc_to_test:
                content = nlp(text)
                d = {}
                for e in content.ents:
                    d[e.label_]=[]
                for e in content.ents:
                    d[e.label_].append(e.text)

                for i in set(d.keys()):
                    print("\n\n")
                    print(i+":"+"\n")
                    for j in set(d[i]):
                        print(j.replace('\n','')+"\n")
                print("##############################################")

                print(parse_to_json(text))

        elif filename[-4:]=='.txt':
            doc_to_test= nlp(txt_sample_to_json(filename)['content'][0])
            #print(doc_to_test)
            #print(txt_sample_to_json(filename)['content'][0])
            d={}
            for ent in doc_to_test.ents:
                d[ent.label_]=[]
            for ent in doc_to_test.ents:
                d[ent.label_].append(ent.text)
            print(d)
            for i in set(d.keys()):
                print("\n\n")
                print(i +":"+"\n")
                for j in set(d[i]):
                    print(j.replace('\n','')+"\n")

            content_token = word_tokenize(txt_sample_to_json(filename)['content'][0])

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
            #print(txt_sample_to_json(filename)['content'][0])
    except:
        for filename in os.listdir('samples_txt'):
            filename = 'samples_txt/'+filename
            if filename[-4:]=='.txt':
                doc_to_test= nlp(txt_sample_to_json(filename)['content'][0])
                #print(doc_to_test)
                #print(txt_sample_to_json(filename)['content'][0])
                d={}
                for ent in doc_to_test.ents:
                    d[ent.label_]=[]
                for ent in doc_to_test.ents:
                    d[ent.label_].append(ent.text)
                print(d)
                for i in set(d.keys()):
                    print("\n\n")
                    print(i +":"+"\n")
                    for j in set(d[i]):
                        print(j.replace('\n','')+"\n")

                content_token = word_tokenize(txt_sample_to_json(filename)['content'][0])

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
