# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 23:55:14 2020

@author: James Ang
"""

import json
import requests
from truck_push_lib import Allocations, Warehouses, Trucks, Suppliers, Routes, Entities, retjson
  
# Opening JSON file 
f = open('input_truck_push.json',)

# g = open('input_leadtime.json',) 
  
data_json = json.load(f)
# data_json2 = json.load(g)

data_allocation = data_json.get('bi-weekly_allocation')

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
