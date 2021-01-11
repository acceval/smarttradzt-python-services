# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 17:40:47 2020

@author: User
"""

import camelot
import time

def allowed_file(filename, ALLOWED_EXTENSIONS):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def scrape_invoice(
        PDF_file,
        doc_type,
        start_time,  
        UPLOAD_FOLDER, 
        ALLOWED_EXTENSIONS
        ):
    
    #%%
    tables = camelot.read_pdf(PDF_file,
                              pages="1", 
                              flavor="stream",                          
                              table_areas=[
                                   "76, 670, 277, 655",     # Title
                                   "374, 367, 420, 355",    # Unit Price
                                   "463, 336, 509, 324",    # Invoice Price      
                                 ],
                              # row_tol=[70,70],
                              # process_background=False
                              )
    # tables
    
    #%% Page 1
    entries1 = [
        "document_title",
        "unit_price (MYR/MT)",    
        "total_price (MYR)",
        ]
    
    retJSON = {}
    
    for i in range(0,len(tables)):
        if tables[i].shape[1] >1:
            a = []
            for j in tables[i].data:
                a.append(" ".join(j))            
            retJSON.update({entries1[i]:" ".join(a)})
        else:
            retJSON.update({entries1[i]:" ".join(tables[i].df[0][:])})
    
    stop_time=time.time() - start_time
    print(f'It takes {round(stop_time,2)} seconds to complete')
    retJSON.update({f"time_taken":str(round(stop_time,2))})
    retJSON.update({"document_type":doc_type})
    
    # for x,y in retJSON.items():
    #     print(x + ':    ' + y + '\n')
    
    return retJSON