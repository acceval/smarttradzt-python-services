#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 16:26:22 2020

@author: alfred
"""
from ws_lib_v3 import indplas,aliba,linkedin
import requests


def background_task(url1,searched_word,url3,job_fcn,sen_level):         
        
    indplas(url1, searched_word)
    # aliba(url2, searched_word)
           
    #%% Linkedin
    
    name,position,location,company,searched_keyword,email \
        = linkedin(url3,searched_word,job_fcn,sen_level)
        
    #%% Send JSON Output
    
    retJSON=[]
    
    for i in range(0,len(name)):
        
        retJSON.append(
            {
                'Contact':name[i],
                'Position':position[i],
                'Company':company[i], 
                'Location':location[i], 
                'Product Keyword': searched_keyword[i],
                'email':email[i]
                }
            )
    
    res = requests.post('http://office.smarttradzt.com:2000/tests/endpoint', json=retJSON)
    print ('response from server:',res.text)
    print(retJSON)
    
    return retJSON