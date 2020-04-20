#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:49:39 2020

@author: alfred
"""
import requests
from flask import request
from lc_lib import request_file, page2text, extract
# import time

def background_task(dpi,pages,PDF_file,poss_lc_list,start_time):         
        
    #%% Part #1 - Convert and store images of each page of PDF file
    # Part #2 - Recognizing text from the images using OCR """
                
    outfile, word_lc = page2text(PDF_file,pages,dpi,poss_lc_list)
            
    #%% Part #3 - Initialisation                  
    # Part #4 - Extract Information from text file"""
            
    retJSON = extract(outfile, word_lc, start_time)
    
    # res = requests.post('http://office.smarttradzt.com:2000/tests/endpoint', json=retJSON)
    res = requests.post('http://127.0.0.1:2000/tests/endpoint', json=retJSON)
    print ('response from server:',res.text)
    # print(retJSON)
    
    return retJSON
