import os
import sys

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter#process_pdf
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

from nltk.tokenize import word_tokenize
import wordsegment

from io import StringIO
import re
from collections import Counter

def pdf_to_text(pdfname):

    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Extract text
    fp = open(pdfname, 'rb')
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    fp.close()

    # Get text from StringIO
    text = sio.getvalue()

    # Cleanup
    device.close()
    sio.close()

    return text

def clean(text):
    text = text.replace('\\n','   ')
    text = text.replace('\\t','  ')
    text = re.sub(r"[\\]\S+","  ",text)
    #ls = re.findall('[a-z]+', text.lower())
    ls = word_tokenize(text)
    lm = []
    wordsegment.load()
    for word in ls:
        l = wordsegment.segment(word)
        if isinstance(l, list):
            lm.extend(l)
        else:
            lm.append(l)
    text = " ".join(lm)

    return text

def parser(pdf_path):
    if pdf_path[-4:] == '.pdf':
        text = str(pdf_to_text(pdf_path).encode("utf-8"))
        text = re.sub(r"[\\]\S+"," ",text[2:50])+clean(text[50:])
        return text
    else:
        print('Invalid filetype error!')
        return None

if __name__=="__main__":
    try:
        pdfname = sys.argv[1].split('\\')[-1]
        if pdfname[-4:]=='.pdf':
            with open('samples_txt/'+pdfname[:-4]+'.txt','w') as f:
                wr = str(pdf_to_text('samples/'+pdfname).encode("utf-8"))
                wr = re.sub(r"[\\]\S+","  ",wr[2:50])+clean(wr[50:])
                f.write(wr)
                print(wr)
    except:
        for pdfname in os.listdir('samples'):
            if pdfname[-4:]=='.pdf':
                with open('samples_txt/'+pdfname[:-4]+'.txt','w') as f:
                    wr = str(pdf_to_text('samples/'+pdfname).encode("utf-8"))
                    wr = re.sub(r"[\\]\S+","  ",wr[2:50])+clean(wr[50:])
                    f.write(wr)
