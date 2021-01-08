# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:31:30 2020

@author: James Ang
"""
from flask import Flask, request
from flask_restful import Resource, Api
import sys
import requests
import pandas as pd
from inv_reg_lib import Inventory_Reg, Regression_Calc, retjson
app = Flask(__name__)
api = Api(app)

#%% Set Upload Folder and Secret Key

if sys.platform == "win32":    
    UPLOAD_FOLDER = r'C:\Users\User\Documents\James\E_BL_LC\LC\alfred\upload'
else:    
    # UPLOAD_FOLDER = r'/home/alfred/uploads'
    UPLOAD_FOLDER = r'/home/alfred/Documents/deploy/lc_bl_inv/uploads'


#%% Endpoint '/' - to test connection

class index(Resource):
    def get(self):
        return request.url

#%% Endpoint '/vaccine_drp'

class drp_push(Resource):
    
    def post(self):
        
        data_json = request.get_json()
        
        #print(dat.get('hospitals'))   

        data_inv = data_json.get('past_inventories')
        
        # data_warehouses = data_json.get('warehouses')
        
        #%% 
        inv_reg_all = [Inventory_Reg(data) for data in data_inv]
        
        reg_all = Regression_Calc(inv_reg_all)
        
        #%% Extracting
        
        retJSON = retjson(reg_all)

        
        return retJSON

api.add_resource(index, '/')
api.add_resource(drp_push, '/inv_reg')

if __name__ == '__main__':
    app.run(debug=True)