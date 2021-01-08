# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 19:04:23 2020

@author: James Ang
"""

import json
import pandas as pd
from vaccine_drp_push_lib import Hospital, Warehouse, Supplier
  
# Opening JSON file 
f = open('input_drp_push.json',) 
  
data = json.load(f)

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