# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 08:20:05 2020

@author: James Ang
"""

import json
import math
import copy
import pandas as pd
import numpy as np
# from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

class Inventory_Reg:
    
    def __init__(self, data):
        
        self.data = data
        
        # self.date_str = self.data.get("datetime_receive_goods_after_quarantine")  
        # self.format_date = "%d-%m-%Y %H:%M"
        # self.datetime_receive_allocation = datetime.strptime(self.date_str, self.format_date)
        
        # self.numdays = 5
        # self.date_truncated = datetime.date(self.datetime_receive_allocation)
        # self.date_range = [self.date_truncated + timedelta(days=x) for x in range(self.numdays)] # Input as date range?
        # self.allocation = self.data.get("allocation")

class Regression_Calc:
    
    def __init__(self, data):
        
        self.data = data
        self.quantity = [int(item.data.get('quantity')) for item in self.data]
        y = self.quantity
        # self.date = [int(item.data.get('date')) for item in self.data]
        self.len_days = list(range(0,len(data)))
        x = np.array(self.len_days).reshape(-1, 1)
        self.model = LinearRegression()
        self.model.fit(x, y)
        y_pred = self.model.predict(x)
        # print(y_pred)
        
        self.difference = int(np.diff(y_pred).mean())
                
        
        
        # self.name = self.data.get('name')
        # self.current_location =self.data.get('current_location')
        # self.current_location_zipcode = self.data.get('current_location_zipcode')
        # self.min_lotsize = self.data.get('min_lotsize')
        # self.max_lotsize = self.data.get('max_lotsize')
        # self.truck_type = self.data.get('truck_type')
        # self.max_daily_delivery_hours = self.data.get('max_daily_delivery_hours')
        # # df.to_dict('series')
        
# class Warehouses:
    
#     def __init__(self, data, allocation):
        
#         self.data = data
#         self.name = self.data.get('name')
#         self.zipcode = self.data.get('zipcode')
#         self.warehouses_supplyto =  self.data.get('supply_to')
        
#         self.hosp_allocation = allocation[0].allocation         #object
#         # self.hosp_alloc = self.hosp_allocation.allocation
        
#         self.warehouse_breakdown = []
        
#         for item in self.hosp_allocation :
#             if item.get("name") in self.warehouses_supplyto:
#                 # print(item.get("name"))
#                 self.warehouse_breakdown.append(item)
                
#         self.warehouse_quantity = sum([data.get("quantity") for data in self.warehouse_breakdown])
#         self.warehouse_allocation = [{'name':self.name,'quantity': self.warehouse_quantity, 'zipcode': self.zipcode}]
        
# class Suppliers:
    
#     def __init__(self, data, allocation, warehouse):
        
#         self.data = data
#         self.name = self.data.get('name')
#         self.zipcode = self.data.get('zipcode')
#         self.suppliers_supplyto =  self.data.get('supply_to')
        
#         self.warehouse_allocation = [wh.warehouse_allocation[0] for wh in warehouse]
#         self.hosp_allocation = allocation[0].allocation
#         # self.hosp_alloc = self.hosp_allocation.allocation
#         self.datetime_receive_allocation = allocation[0].datetime_receive_allocation
        
#         self.all_allocation = self.hosp_allocation + self.warehouse_allocation
        
#         self.supplier_breakdown = []
        
#         for item in self.all_allocation :
#             if item.get("name") in self.suppliers_supplyto:
#                 # print(item.get("name"))
#                 self.supplier_breakdown.append(item)


# def intersperse(lst, item):
#     result = [item] * (len(lst) * 2 - 1)
#     result[0::2] = lst
#     return result


def retjson(reg_all):
    
    keys_to_extract = [
    'difference',
    # 'route_name',
    # 'route_truck_name',
    # 'schedules',
    ]
    
    # reg_out = [reg.__dict__[keys] for keys in keys_to_extract for reg in [reg_all]]
    
    # reg_out = [reg_all.__dict__[keys] for keys in keys_to_extract]
    
    reg_out = reg_all.__dict__[keys_to_extract[0]]
    
    retJSON = {
    "difference": reg_out,
    # "warehouses": warehouse_out,
    # "suppliers": supplier_out,
            }
    return retJSON