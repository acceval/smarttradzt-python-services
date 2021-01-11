# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:31:30 2020

@author: James Ang
"""
from flask import Flask, request, jsonify, flash, redirect
from flask_restful import Resource, Api
import sys
import time
from werkzeug.utils import secure_filename
import os
import camelot
import redis
from rq import Queue


from lc_lib1 import request_file, page2text, extract
from bl_lib1 import bl_scrape1
from invoice_lib1 import scrape_invoice
from va6_lib import va
from pro_opt_back import background_task


app = Flask(__name__)
api = Api(app)

r = redis.Redis() # create redis client using default 6379
q = Queue(connection=r)#, serializer=dill)



#%% Set Upload Folder and Secret Key

if sys.platform == "win32":    
    UPLOAD_FOLDER = r'C:\Users\User\Documents\James\E_BL_LC\LC\alfred\upload'
else:    
    # UPLOAD_FOLDER = r'/home/alfred/uploads'
    UPLOAD_FOLDER = r'/home/alfred/Documents/deploy/lc_bl_inv/uploads'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "smarttradzt"
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename, ALLOWED_EXTENSIONS):
    
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#%% Image resolution dots-per-inch (dpi)
dpi = 180

# LC comparison list
lc_list =[
            'Letter of Credit',
            'LC',
            'L/C',
            'DLC',
            'Documentary Letter of Credit',
            'Documentary Credit',
            'Credit Slip'
            ]

bl_list =[
            'Bill of lading',
            'BL',
            'B/L',
            'Waybill',
            'Consignment Note',
            'Shipping bill',
            'Transport Document',
            'Freight Bill',
            'Cargo Manifest',
            'Transport Document',            
            ]

inv_list =[
            'Commercial Invoice',
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
        
        if 'file' not in request.files:
            flash('No file part')        
            return redirect(request.url) , 201
        
        file = request.files['file']
        if file.filename == '':            
            flash('No file selected for uploading')            
            return redirect(request.url) , 202
	
        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):        
            if sys.platform == "win32":            
                PDF_file = UPLOAD_FOLDER+'\\'+ secure_filename(file.filename)
            
            else:           
                PDF_file = UPLOAD_FOLDER+'/'+ secure_filename(file.filename)
            
            file.save(os.path.join(UPLOAD_FOLDER, PDF_file))
       
        # read 1st page
        tables = camelot.read_pdf(PDF_file,
                          pages="1",
                          flavor="stream",
                          )
        doc_type = []

        for word in lc_list:
            # print(word)
            if word.lower() in " ".join(tables[0].df[0][1:10]).lower():        
                print(f'"{word}" is found in Document. Document is possibly a Letter of Credit.')
                doc_type = "LC"
                pages = request_file(PDF_file, dpi)                
            
                #%% Part #1 - Convert and store images of each page of PDF file
                # Part #2 - Recognizing text from the images using OCR """
                    
                outfile = page2text(PDF_file,pages,dpi,lc_list)
                
                #%% Part #3 - Initialisation                  
                # Part #4 - Extract Information from text file"""
                
                retJSON = extract(outfile, doc_type, start_time)
                break
        #%%
        if doc_type==[]:
            for word in bl_list:
                if word.lower() in " ".join(tables[0].df[0][1:10]).lower():        
                    print(f'"{word}" is found in Document. Document is possibly a Bill of Lading.')
                    doc_type = "BL"
                    retJSON = bl_scrape1(PDF_file,start_time, doc_type)
                    # print(word.lower())
                    break
        
        if doc_type==[]:
            for word in inv_list:
                if word.lower() in " ".join(tables[0].df[0][1:20]).lower():        
                    print(f'"{word}" is found in Document. Document is possibly a Commercial Invoice.')
                    doc_type = "Invoice"
                    retJSON = scrape_invoice(
                        PDF_file,
                        doc_type,
                        start_time,  
                        UPLOAD_FOLDER, 
                        ALLOWED_EXTENSIONS
                        )
                    break        
        
        #%% 
        # if doc_type =="BL":
            
        #     retJSON = bl_scrape1(PDF_file,start_time, doc_type)
            
        # elif doc_type =='LC':
            
        #     #%% Get File
        #     pages = request_file(PDF_file, dpi)                
            
        #     #%% Part #1 - Convert and store images of each page of PDF file
        #     # Part #2 - Recognizing text from the images using OCR """
                    
        #     outfile = page2text(PDF_file,pages,dpi,lc_list)
                
        #     #%% Part #3 - Initialisation                  
        #     # Part #4 - Extract Information from text file"""
                
        #     retJSON = extract(outfile, doc_type, start_time)
        
        # elif doc_type =='Invoice':
            
        #     retJSON = scrape_invoice(
        #     PDF_file,
        #     doc_type,
        #     start_time,  
        #     UPLOAD_FOLDER, 
        #     ALLOWED_EXTENSIONS
        #     )
        
        return jsonify(retJSON)

class volume(Resource):
    
    def post(self):
               
        # Start Time
        start_time = time.time()
        
        buyer_request = int(request.form['br'])
        
        sup1_weight = request.form['sup1_tier_weight']
        sup1_tier_weight = [int(x) for x in sup1_weight.split(',')]
        
        sup2_weight = request.form['sup2_tier_weight']
        sup2_tier_weight = [int(x) for x in sup2_weight.split(',')]
        
        sup3_weight = request.form['sup3_tier_weight']
        sup3_tier_weight = [int(x) for x in sup3_weight.split(',')]
        
        sup1_tier = request.form['sup1_tier_price']
        sup1_tier_price = [int(x) for x in sup1_tier.split(',')]
        
        sup2_tier = request.form['sup2_tier_price']
        sup2_tier_price = [int(x) for x in sup2_tier.split(',')]
        
        sup3_tier = request.form['sup3_tier_price']
        sup3_tier_price = [int(x) for x in sup3_tier.split(',')]
        
        sup1_vol_appor = request.form['sup1_VA']
        sup1_VA = [float(x) for x in sup1_vol_appor.split(',')]
        
        sup2_vol_appor = request.form['sup2_VA']
        sup2_VA = [float(x) for x in sup2_vol_appor.split(',')]
        
        retJSON = va(
            start_time,
            buyer_request, 
            sup1_tier_weight, 
            sup2_tier_weight, 
            sup3_tier_weight,
            sup1_tier_price,
            sup2_tier_price,
            sup3_tier_price,
            sup1_VA,
            sup2_VA,
            )
                     
        return jsonify(retJSON)

class procure(Resource):    

    def post(self):           

        # Start Time
        start_time = time.time()        

        inv_start_point = int(request.form['inv_start_point'])        

        ini_weig_mat_cost = int(request.form['ini_weig_mat_cost'])        

        num_eval_days = int(request.form['num_eval_days'])        

        inv_min = int(request.form['inv_min'])        

        inv_max = int(request.form['inv_max'])        

        leadtimeA = int(request.form['leadtimeA'])        

        total_volume = int(request.form['total_volume'])        

        perc_purvol_A = int(request.form['percent_purchase_vol_A'])        

        perc_purvol_B = int(request.form['percent_purchase_vol_B'])        

        prA = request.form['weekly_price_A']

        price_A = [int(x) for x in prA.split(',')]        

        prB = request.form['weekly_price_B']

        price_B = [int(x) for x in prB.split(',')]        

        prC = request.form['weekly_price_C']

        price_C = [int(x) for x in prC.split(',')]                     

        job = q.enqueue(background_task, 
                        start_time,
                        inv_start_point,
                        ini_weig_mat_cost,
                        num_eval_days,
                        inv_min,
                        inv_max,
                        leadtimeA,
                        total_volume,
                        perc_purvol_A,
                        perc_purvol_B,
                        price_A,
                        price_B,
                        price_C,    
                        )                     

        return f" Task {job.id} added to queue at {job.enqueued_at}. tasks in the queue."

class receive(Resource):

    def post(self):

        input_json = request.get_json(force=True) 
        # force=True, above, is necessary if another developer 
        # forgot to set the MIME type to 'application/json'

        print (f'data from client:{input_json}')
        
        dictToReturn = {'answer':42}

        return jsonify(dictToReturn)
    

api.add_resource(index, '/')
api.add_resource(upload, '/upload')
api.add_resource(volume, '/volume_apportion')
api.add_resource(procure, '/procure_opt/send')
api.add_resource(receive, '/procure_opt/receive')

if __name__ == '__main__':
    app.run(debug=True)