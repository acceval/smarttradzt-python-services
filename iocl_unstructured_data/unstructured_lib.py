# -*- coding: utf-8 -*-

from flask import request, flash, redirect

from werkzeug.utils import secure_filename
# from textblob.classifiers import NaiveBayesClassifier
import sys
import os
import json
import PyPDF2
from textblob import TextBlob
import pandas as pd

#%%
if sys.platform == "win32":    
    UPLOAD_FOLDER = r'C:\Users\User\Documents\ghub_acceval\smarttradzt-python-services\iocl_unstructured_data\upload'
else:
    UPLOAD_FOLDER = r'/home/alfred/Documents/deploy/lc_bl_inv/uploads'

#%%
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename, ALLOWED_EXTENSIONS):
    
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def calc(cl, req):
    
    col = []
    df = []
    sent = []
    pp = []
    
    # data = request.get_json()
    if 'file' not in req:
        flash('No file part')        
        return redirect(request.url) , 201
    
    file = req['file']
    if file.filename == '':            
        flash('No file selected for uploading')            
        return redirect(request.url) , 202
	
    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):        
        if sys.platform == "win32":            
            PDF_file = UPLOAD_FOLDER+'\\'+ secure_filename(file.filename)
        
        else:           
            PDF_file = UPLOAD_FOLDER+'/'+ secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, PDF_file)
        file.save(path)
    # print(path)
    # print(type(path))
    
    pdfFileObj = open(path, 'rb')

    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    totalpage = pdfReader.numPages
    print(totalpage)
    
    pg = [''] * (totalpage-2-2)
    for i in [x for x in range(2,totalpage-2) if x != 7]:
        # print(i)
        pageObj = pdfReader.getPage(i)
        pg[i-2] = pageObj.extractText().replace("\n","").lower()
        
    pg.remove("")
    
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
            # col.append(sentence.classify())
    pos_percentage = col.count('pos')/len(col)
    
    if int(pos_percentage*100) <= 30:
        doc_sentiment = "negative"
    elif int(pos_percentage*100) <= 70:
        doc_sentiment = "neutral"
    else:
        doc_sentiment = "positive"
        
    pp.append(int(pos_percentage*100))
    
    print(file.filename)
    print(pp)
    
    #%% extracting   
    sentence_summary = pd.DataFrame({'sentences':sent, 'classification': col})
    summary = pd.DataFrame({'filename':file.filename, 'percentage_positive':pp, "overall_doc_sentiment": doc_sentiment})
    # print(sentence_summary)
    summary = json.loads(summary.to_json(orient='records'))
    sentence_summary = json.loads(sentence_summary.to_json(orient='records'))
    
    return summary, sentence_summary

def retjson(summary,sentence_summary):
    
    # keys_to_extract = [
    #     'origin_country',
    #     'destination_country',
    #     'destination_airport',
    #     'container_type_qty_and_schedule',
    #     ]
        
    # allocation_out =[{key: item.__dict__[key] for key in keys_to_extract} for item in allocation_all]
    
    
    retJSON = {"overall_sentiment": summary,
                "sentence_sentiment": sentence_summary
                # "warehouses": warehouse_out,
                # "suppliers": supplier_out,
                # "dryice_suppliers": dryice_out
                }
    
    return retJSON