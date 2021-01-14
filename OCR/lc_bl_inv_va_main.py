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

from lc_lib import request_file, page2text, extract, scan_image
from bl_lib import bl_scrape
from invoice_lib import scrape_invoice
from va_lib import va


app = Flask(__name__)
api = Api(app)

#%% Set Upload Folder and Secret Key

if sys.platform == "win32":    
    UPLOAD_FOLDER = r'C:\Users\User\Documents\ghub_acceval\smarttradzt-python-services\OCR\uploads'
    UPLOAD_FOLDER1 = r'C:\Users\User\Documents\ghub_acceval\smarttradzt-python-services\OCR'
    
else:    
    # UPLOAD_FOLDER = r'/home/alfred/uploads'
    UPLOAD_FOLDER = r'/home/alfred/Documents/deploy/lc_bl_inv2/uploads'
    UPLOAD_FOLDER1 = r'/home/alfred/Documents/deploy/lc_bl_inv2'



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
            'Invoice',
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
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            if file_ext == 'pdf':
                if sys.platform == "win32":            
                    PDF_file = UPLOAD_FOLDER+'\\'+ secure_filename(file.filename)
                
                else:           
                    PDF_file = UPLOAD_FOLDER+'/'+ secure_filename(file.filename)
            elif file_ext == 'jpg' or file_ext == 'png':
                if sys.platform == "win32":            
                    PDF_file = UPLOAD_FOLDER1+'\\'+ secure_filename(file.filename)
                
                else:           
                    PDF_file = UPLOAD_FOLDER1+'/'+ secure_filename(file.filename)
            else:
                pass
            
            if file_ext == 'pdf':
                file.save(os.path.join(UPLOAD_FOLDER, PDF_file))
            elif file_ext == 'jpg' or file_ext == 'png':
                file.save(os.path.join(UPLOAD_FOLDER1, PDF_file))
            else:
                pass
            


        # read 1st page
        if file_ext == 'pdf':
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
                        retJSON = bl_scrape(PDF_file,start_time, doc_type)
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
        elif file_ext == 'jpg' or file_ext == 'png':

            #doc_type = "LC"

            retJSON = scan_image(file.filename, file_ext, start_time)

        else:
            pass    
            
            
            #retJSON = extract2(outfile, doc_type, start_time)
            
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


api.add_resource(index, '/')
api.add_resource(upload, '/upload')
api.add_resource(volume, '/volume_apportion')

if __name__ == '__main__':
    app.run(debug=True)