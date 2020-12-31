# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:31:30 2020

@author: James Ang
"""
from flask import Flask, request, jsonify, flash, redirect
from flask_restful import Resource, Api
import sys
import pandas as pd
from vaccine_drp_push_lib import Hospital, Warehouse, Supplier

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
        
        data = request.get_json()
        
        #print(dat.get('hospitals'))   

        data_hospitals = data.get('hospitals')

        data_warehouse = data.get('warehouses')

        data_supplier = data.get('suppliers')

        #%%

        hospitals_all = [Hospital(data) for data in data_hospitals]

        warehouse_all = [Warehouse(data) for data in data_warehouse]

        supplier_all = [Supplier(data, hospitals_all, warehouse_all) for data in data_supplier]

        #%%
        keys_to_extract = [
            'name',
            'table_final'
                        ]
        hosp_out =[{key: hosp.__dict__[key] for key in keys_to_extract} for hosp in hospitals_all]
        warehouse_out =[{key: wh.__dict__[key] for key in keys_to_extract} for wh in warehouse_all]
        supplier_out = [{key: supp.__dict__[key] for key in keys_to_extract} for supp in supplier_all]


        retJSON = {"hospitals": hosp_out,
            "warehouses": warehouse_out,
            "suppliers": supplier_out,
            }
        return retJSON

api.add_resource(index, '/')
api.add_resource(drp_push, '/vac_drp_push')

if __name__ == '__main__':
    app.run(debug=True)