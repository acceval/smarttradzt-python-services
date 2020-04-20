# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:31:30 2020

@author: James Ang
"""
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from lc_lib import request_file

import sys
import time
# from lc_lib import request_file, page2text, extract

import redis
from rq import Queue
from lc_back19 import background_task

app = Flask(__name__)
api = Api(app)

#%% redis
r = redis.Redis() # create redis client using default 6379
q = Queue(connection=r)#, serializer=dill)

#%% Set Upload Folder and Secret Key

if sys.platform == "win32":    
    UPLOAD_FOLDER = r'C:\Users\User\Documents\James\E_BL_LC\LC\alfred\upload'
else:    
    UPLOAD_FOLDER = r'/home/jamesv2/Desktop/web/LC/uploads'
    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "smarttradzt"
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

#%% Image resolution dots-per-inch (dpi)
dpi = 180

# LC comparison list
poss_lc_list =[
            'Letter of Credit',
            'LC',
            'L/C',
            'DLC',
            'Documentary Letter of Credit',
            'Documentary Credit',
            'Credit Slip'
            ]
       
#%% Endpoint '/' - to test connection

class index(Resource):
    def get(self):
        return request.url

#%% Endpoint '/upload'

class upload(Resource):
    
    def post(self):
               
    # Start Time
        start_time = time.time()
        
        # # Get DPI
        # dpi = request.form['dpi']        
        # if dpi == "":            
        #     dpi = 300            
        #     flash("No DPI value provided. Set to default: 300")
        
        #%% Get File
        pages,PDF_file = request_file(request.files, dpi, UPLOAD_FOLDER, ALLOWED_EXTENSIONS)                
        job = q.enqueue(background_task, dpi,pages,PDF_file,poss_lc_list,start_time)
                
        return f" Task {job.id} added to queue at {job.enqueued_at}. tasks in the queue."

api.add_resource(index, '/')
api.add_resource(upload, '/upload')

if __name__ == '__main__':
    app.run(debug=True)