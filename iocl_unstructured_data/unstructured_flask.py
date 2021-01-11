# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:31:30 2020

@author: James Ang
"""
from flask import Flask, request, flash, redirect, jsonify
from flask_restful import Resource, Api
# from werkzeug.utils import secure_filename
from textblob.classifiers import NaiveBayesClassifier
import sys
# import os
# import PyPDF2
# from textblob import TextBlob
# import pandas as pd
# import requests
from unstructured_lib import calc, retjson#allowed_file

app = Flask(__name__)
api = Api(app)

#%% Set Upload Folder and Secret Key

if sys.platform == "win32":    
    UPLOAD_FOLDER = r'C:\Users\User\Documents\ghub_acceval\smarttradzt-python-services\iocl_unstructured_data\upload'
else:
    UPLOAD_FOLDER = r'/home/alfred/Documents/deploy/lc_bl_inv/uploads'

#%%
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#%%
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

cl = NaiveBayesClassifier(train)


#%% Endpoint '/' - to test connection

class index(Resource):
    def get(self):
        return request.url

#%% Endpoint '/'

class unstructured(Resource):
    
    def post(self):
        
        summary, sentence_summary = calc(cl,request.files)

        retJSON = retjson(summary, sentence_summary)

        return retJSON

api.add_resource(index, '/')
api.add_resource(unstructured, '/unstructured')

if __name__ == '__main__':
    app.run(debug=True)