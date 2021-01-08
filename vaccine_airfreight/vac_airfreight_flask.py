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
from vac_airfreight_lib import Container, Allocation, retjson

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

class vac_freightdrp(Resource):
    
    def post(self):
        
        data = request.get_json()
        data_allocation = data.get('monthly_allocation')

        response = requests.get("https://office.smarttradzt.com:8001/buy-shopping-service/container/findAll")
        
        data_containers = response.json()
        
        
        #%%
        containers_all = [Container(data) for data in data_containers]
        
        allocation_all = [Allocation(data, containers_all) for data in data_allocation]
        
        #%% extracting
        
        retJSON = retjson(allocation_all)

        return retJSON

api.add_resource(index, '/')
api.add_resource(vac_freightdrp, '/vac_airfreight_container')

if __name__ == '__main__':
    app.run(debug=True)