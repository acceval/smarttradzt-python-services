# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 01:35:00 2020

@author: James Ang
"""
import json
import pandas as pd
from vaccine_drp_lib import Hospital, Demand_Centre, Supplier, Dry_Ice_Supplier
  
# Opening JSON file 
f = open('input_demo.json',) 
  
# returns JSON object as  
# a dictionary 
data = json.load(f)

data_hospitals = data.get('hospitals')

data_warehouse = data.get('warehouses')

data_supplier = data.get('suppliers')

data_dryice = data.get('dryice_suppliers')
#%%




hosp_1 = Hospital(data_hospitals, hosp_num = 0)
order_hosp_1 = hosp_1.calc()

hosp_2 = Hospital(data_hospitals, hosp_num = 1)
order_hosp_2 = hosp_2.calc()

hosp_3 = Hospital(data_hospitals, hosp_num = 2)
order_hosp_3 = hosp_3.calc()

hosp_4 = Hospital(data_hospitals, hosp_num = 3)
order_hosp_4 = hosp_4.calc()

hosp_5 = Hospital(data_hospitals, hosp_num = 4)
order_hosp_5 = hosp_5.calc()

#%%
keys_to_extract = ['name','table_final']
subset_hosp1 = {key: hosp_1.__dict__[key] for key in keys_to_extract}
subset_hosp2 = {key: hosp_2.__dict__[key] for key in keys_to_extract}
subset_hosp3 = {key: hosp_3.__dict__[key] for key in keys_to_extract}
subset_hosp4 = {key: hosp_4.__dict__[key] for key in keys_to_extract}
subset_hosp5 = {key: hosp_5.__dict__[key] for key in keys_to_extract}


# Warehouse (Juru)
warehouse_demand = pd.Series(order_hosp_4) + pd.Series(order_hosp_5)
warehouse = Demand_Centre(data_warehouse,warehouse_demand)
order_warehouse = warehouse.calc()


# Supplier
supply_demand = pd.Series(order_hosp_1) + pd.Series(order_hosp_2) + pd.Series(order_hosp_3) + pd.Series(order_warehouse)
supplier = Supplier(data_supplier, supply_demand)
order_supplier = supplier.calc()

# Dry ice Supplier - Sourcing plan
dry_ice_demand = pd.Series(order_supplier)
dry_ice_supplier = Dry_Ice_Supplier(data_dryice, dry_ice_demand)
dry_ice_supplier.calc()

collect = [subset_hosp1, subset_hosp2, subset_hosp2,]

retJSON = json.dumps(subset_hosp1)
