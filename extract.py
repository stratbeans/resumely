import pdftotext

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
import string
import re

from skilldatabase import skillDB

class SkillExtractor:
    skillArray = []
    def __init__(self):
        pass

    def parse(self, resumePDF):
        # Open the file
        with open(resumePDF, "rb") as f:
            pdf = pdftotext.PDF(f)

        resumeString = ''.join(pdf);

        stopWords = set(stopwords.words('english'))

        wordToken = word_tokenize(resumeString)

        filtered_sentence = []
        for w in wordToken:
            if w not in stopWords:
                    filtered_sentence.append(w)
        d = TreebankWordDetokenizer()
        f = d.detokenize(filtered_sentence)

        remove = string.punctuation
        pattern = r"[{}]".format(remove) # create the pattern
        f = re.sub(pattern, "", f)
        f = f.lower()

        self.skillArray = f.split()

    def extractSkills(self):
        #print self.skillArray
        #print skillDB

        outputCategory = {}
        for skill in self.skillArray:
            for category, sArray in skillDB.items():
                if skill not in sArray:
                    continue
                if category in outputCategory:
                    if skill in outputCategory[category]:
                        continue
                    outputCategory[category].append(skill)
                else :
                    outputCategory[category] = [skill]
                        
        for key, value in outputCategory.items():
            print key + " : " + ', '.join(value)
