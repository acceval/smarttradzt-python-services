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
from truck_push_lib import Allocations, Warehouses, Trucks, Suppliers, Routes, Entities, retjson

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

        data_allocation = data_json.get('weekly_allocation')

        data_warehouses = data_json.get('warehouses')
        
        data_suppliers = data_json.get('suppliers')
        
        # data_entities = data_json2.get('entity_properties')
        
        data_trucks = data_json.get('trucks')
        
        data_routes = data_json.get('routes')
        
        # API
        response = requests.get("https://office.smarttradzt.com:8001/buy-ecommerce-service/lead-time/delivery/findAll/202012120000195")
        
        data_entities = response.json()
        
        #%% 
        allocation_all = [Allocations(data) for data in data_allocation]
        
        warehouse_all = [Warehouses(data, allocation_all) for data in data_warehouses]
        
        trucks_all = [Trucks(data) for data in data_trucks]
        
        supplier_all = [Suppliers(data, allocation_all, warehouse_all) for data in data_suppliers]
        
        entity_property = [Entities(data) for data in data_entities]
        
        routes_all = [Routes(data, entity_property, supplier_all, trucks_all) for data in data_routes]
        
        #%% Extracting
        
        retJSON = retjson(routes_all)
        
        return retJSON

api.add_resource(index, '/')
api.add_resource(drp_push, '/vac_truck_push')

if __name__ == '__main__':
    app.run(debug=True)