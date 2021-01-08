# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 23:55:14 2020

@author: James Ang
"""

import json
import requests
from inv_reg_lib import Inventory_Reg, Regression_Calc, retjson
  
# Opening JSON file 
f = open('input.json',)
  
data_json = json.load(f)

data_inv = data_json.get('past_inventories')

# data_warehouses = data_json.get('warehouses')

#%% 
inv_reg_all = [Inventory_Reg(data) for data in data_inv]

reg_all = Regression_Calc(inv_reg_all)

#%% Extracting

retJSON = retjson(reg_all)

print(retJSON)
