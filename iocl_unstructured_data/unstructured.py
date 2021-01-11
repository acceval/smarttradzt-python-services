# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 11:03:23 2019

Method:
    1) Using Mr Osman's input, train a Naive Bayesian classifier.
    2) The test is applied directly on every single raw sentence in every page of the document
    3) The ratio of positive to the number of total sentences are calculated, with the assumption,
        that if the ratio is higher, then the stock market will increase. If there are more
        negative sentences then the stock market will drop.
Loop holes:
    1) Not all sentences are useful.
    2) We're predicting ME UREA price, hence the relevant sentiment must only be
        related to ME.
    3) Not all words are necessary for analysis. e.g stop words etc.

Future work:
    1) should we focus on particular page, or paragraph only in the document?
    2) or should we get more data from other new sources? This will make things more complex.
    3) TFIDF - used to evaluate how important a word is to a document (the originality of the word)
    4) LDA to identify latent topics? use Topic Kullback-Leibler (KL) to determine number of topics.
        Larger the KL Divergence, the better performance the LDA model yields.
    5) use Bi-grams? i.e 2 words in stead of one?
    6) Try other classifiers other than Naive Bayesian?
    7) time lag between release of news and actual effect?
    
@author: James Ang
"""
# Supervised learning

# =============================================================================
# First step, train the classifier using Osman's input.
# =============================================================================
train = [
     ('Bullish Former Soviet Union', 'pos'),
     ('Firmer sentiment United States', 'pos'),
     ('Inexpensive credit brazil', 'pos'),
     ('Requirement for prompt position brazil', 'pos'),
     ('Outages Egypt ruptured pipeline', 'pos'),
     ('urea bins exhausted Americas', 'pos'),
     ('market reached a floor  canada', 'pos'),
     ('extra credit brazil bank', 'pos'),
     ('corn prices up brazil', 'pos'),
     ('soya harvest complete brazil', 'pos'),
     ('demand for blending china', 'pos'),
     ('lunar holidays Asia', 'neg'),
     ('Indonesia switch from urea exports to ammonia', 'neg'),
     ('revised tender Former Soviet Union', 'neg'),
     ('Contract cargoes destined for Thailand', 'neg'),
     ('revised tender Former Soviet Union', 'neg'),
     ('china spring lunar festival', 'neg'),
     ('Spring planting of corn and other crops', 'pos'),
     ('winter wheat fields of the southern US', 'neg'),
     ('pressure from buyers USA', 'neg'),
     ('spring crop earlier USA', 'pos'),
     ('earlier  demand potash and phosphate USA', 'pos'),
     ('demand for spring application is up substantially China', 'pos'),
     ('spot activities insginificant Middle east', 'neg'),
     ('prevailing draught stopped urea activities Thailand', 'neg'),
     ('hold off on purchases Europe', 'neg'),
     ('demand for wheat application France', 'pos'),
     ('preplant urea Midwest USA', 'pos'),
     ('trader cautious black sea', 'neg')]

test = [
     ('cuts in output anywhere', 'pos'),
     ('sellers chasing prompt and forward business USA ', 'neg'),
     ('competition for business fierce USA', 'neg'),
     ('significant surge in demand anywhere', 'pos'),
     ('expecting further discounts Brazil', 'pos'),
     ('limited outlets and decreasing netbacks from domestic sales in China', 'neg') ]

#test = [
#...     ('Spring planting of corn and other crops', 'pos'),
#...     ('winter wheat fields of the southern US', 'neg'),
#...     ('pressure from buyers USA', 'neg'),
#...     ('spring crop earlier USA', 'pos'),
#...     ('earlier  demand potash and phosphate USA', 'pos'),
#...     ('trader cautious black sea', 'neg')]


from textblob.classifiers import NaiveBayesClassifier
cl = NaiveBayesClassifier(train)

# cl.accuracy(test)

# cl.show_informative_features(5)

# =============================================================================
# Section 2
# =============================================================================
import pandas as pd
import PyPDF2
#import gensim
from textblob import TextBlob
#from nltk.stem import WordNetLemmatizer, SnowballStemmer
#stemmer = SnowballStemmer("english")
import os

directory = os.fsencode(r'C:\Users\User\Documents\ghub_acceval\smarttradzt-python-services\iocl_unstructured_data')

col = []
df = []
fname = []
sent = []
pp = []   # Percentage Positive
for file_name in os.listdir(directory):
    if file_name.endswith(b".pdf"):      # getting all pdf files
        fn = file_name.decode('utf-8')
        print(fn)
        fname.append(fn)
#        print(fn)
#        print(os.path.join(directory, filename))
        path = os.path.join(directory, file_name)
        
        # =====================================================================
        # Extracting text from pdf files
        # =====================================================================
        pdfFileObj = open(path, 'rb')

        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        totalpage = pdfReader.numPages
        
        pg = [''] * (totalpage-2-2)
        for i in [x for x in range(2,totalpage-2) if x != 7]:
            # print(i)
            pageObj = pdfReader.getPage(i)
            pg[i-2] = pageObj.extractText().replace("\n","").lower()
            
        pg.remove("")
        
        # =============================================================================
        # Evaluation on actual UREA data
        # =============================================================================
        for doc in pg:
#            print (doc)
            blob = TextBlob(doc,classifier=cl)  # put trained classifier in here.
    
            for sentence in blob.sentences:
                # print(sentence)
                # print(sentence.classify())
                if "www.crugroup.com" in sentence:
                    pass
                else:
                    sent.append(sentence.string)
                    col.append(sentence.classify())
        pos_percentage = col.count('pos')/len(col)
        
        if int(pos_percentage*100) <= 30:
            doc_sentiment = "negative"
        elif int(pos_percentage*100) <= 70:
            doc_sentiment = "neutral"
        else:
            doc_sentiment = "positive"
        
        pp.append(int(pos_percentage*100))
        
        continue
    else:
        continue

sent_summary = pd.DataFrame({'Sentences':sent, 'classification': col})
summary = pd.DataFrame({'Filename':fname, 'Percentage_positive':pp, "overall sentiment": doc_sentiment})
print(summary)
# =============================================================================
#                                Filename  Percentage_positive
# 0  FW Urea Weekly Report 02-04-2016.pdf             0.684211
# 1     Urea Weekly Report 02-11-2016.pdf             0.693617
# 2     Urea Weekly Report 02-18-2016.pdf             0.693593
# 3     Urea Weekly Report 02-25-2016.pdf             0.695833
# =============================================================================
