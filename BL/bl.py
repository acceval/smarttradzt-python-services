

from flask import Flask, request, flash, redirect
from flask_restful import Resource, Api

from werkzeug.utils import secure_filename
from pdf2image import convert_from_path 

import sys
import os

app = Flask(__name__)
api = Api(app)

dpi = 180
UPLOAD_FOLDER = r'/home/jamesv2/Desktop/bl/uploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename, ALLOWED_EXTENSIONS):
    
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def request_file(f, dpi, UPLOAD_FOLDER, ALLOWED_EXTENSIONS):
    
    if 'file' not in f:        
        flash('No file part')        
        return redirect(request.url) , 201    
    file = request.files['file']
    
    
    if file.filename == '':            
        flash('No file selected for uploading')            
        return redirect(request.url) , 202
    
         
    if file and allowed_file(file.filename,ALLOWED_EXTENSIONS):        
        if sys.platform == "win32":            
            PDF_file = UPLOAD_FOLDER+'\\'+ secure_filename(file.filename)
        
        else:           
            PDF_file = UPLOAD_FOLDER+'/'+ secure_filename(file.filename)
        
        file.save(os.path.join(UPLOAD_FOLDER, PDF_file))
        
        # Store all the pages of the PDF in a variable        
        pages = convert_from_path(PDF_file,
                                  dpi=dpi,
                                  grayscale=True,
                                  thread_count=3,
                                  # size=(1600, None),
                                  # fmt="jpeg",
                                  # output_folder='/home/alfred/uploads2',
                                  # use_cropbox=False,
                                  )

    return pages, PDF_file

class upload(Resource):
    
    def post(self):

        pages,PDF_file = request_file(request.files, dpi, UPLOAD_FOLDER, ALLOWED_EXTENSIONS)