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
from vaccine_drp_lib import Hospital, Demand_Centre, Supplier, Dry_Ice_Supplier

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

class vaccine_drp(Resource):
    
    def post(self):
        
        dat = request.get_json()
        
        #print(dat.get('hospitals'))
   
        data_hospital = dat.get('hospitals')
        data_warehouse = dat.get('warehouses')
        #print(data_warehouse)

        data_supplier = dat.get('suppliers')
        #print(data_supplier)

        data_dryice = dat.get('dryice_suppliers')
        #print(data_dryice)
        
        keys_to_extract = ['name','table_final']

        # Hospital 1
        hosp_1 = Hospital(data_hospital, hosp_num = 0)
        order_hosp_1 = hosp_1.calc()
        subset_hosp1 = {key: hosp_1.__dict__[key] for key in keys_to_extract}

        # Hospital 2
        hosp_2 = Hospital(data_hospital, hosp_num = 1)
        order_hosp_2 = hosp_2.calc()
        subset_hosp2 = {key: hosp_2.__dict__[key] for key in keys_to_extract}

        # Hospital 3
        hosp_3 = Hospital(data_hospital, hosp_num = 2)
        order_hosp_3 = hosp_3.calc()
        subset_hosp3 = {key: hosp_3.__dict__[key] for key in keys_to_extract}

        # Hospital 4
        hosp_4 = Hospital(data_hospital, hosp_num = 3)
        order_hosp_4 = hosp_4.calc()
        subset_hosp4 = {key: hosp_4.__dict__[key] for key in keys_to_extract}

        # Hospital 5
        hosp_5 = Hospital(data_hospital, hosp_num = 4)
        order_hosp_5 = hosp_5.calc()
        subset_hosp5 = {key: hosp_5.__dict__[key] for key in keys_to_extract}
                
        # Warehouse (Juru)
        warehouse_demand = pd.Series(order_hosp_4) + pd.Series(order_hosp_5)
        warehouse = Demand_Centre(data_warehouse, warehouse_demand)
        order_warehouse = warehouse.calc()
        subset_warehouse = {key: warehouse.__dict__[key] for key in keys_to_extract}

        keys_to_extract_supp = ['name','table_final']
        # Supplier
        supply_demand = pd.Series(order_hosp_1) + pd.Series(order_hosp_2) + pd.Series(order_hosp_3) + pd.Series(order_warehouse)
        supplier = Supplier(data_supplier, supply_demand)
        order_supplier = supplier.calc()
        subset_supplier = {key: supplier.__dict__[key] for key in keys_to_extract_supp}

        # Dry ice Supplier - Sourcing plan
        dry_ice_demand = pd.Series(order_supplier)
        dry_ice_supplier = Dry_Ice_Supplier(data_dryice, dry_ice_demand)
        dry_ice_supplier.calc()
        subset_dryice = {key: dry_ice_supplier.__dict__[key] for key in keys_to_extract}

        retJSON = {"hospitals": [
            subset_hosp1, 
            subset_hosp2,
            subset_hosp3,
            subset_hosp4,
            subset_hosp5],
            "warehouses": [subset_warehouse],
            "suppliers": [subset_supplier],
            "dryice_suppliers": [subset_dryice]
            }
        return retJSON

api.add_resource(index, '/')
api.add_resource(vaccine_drp, '/vaccine_drp')

if __name__ == '__main__':
    app.run(debug=True)