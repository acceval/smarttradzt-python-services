# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 01:35:00 2020

@author: James Ang
"""
import json
import requests
from vac_airfreight_lib import Container, Allocation, retjson

# Opening JSON file 
f = open('input_airfreight.json',)
  
# returns JSON object as  
# a dictionary 
data = json.load(f)

data_allocation = data.get('monthly_allocation')

response = requests.get("https://office.smarttradzt.com:8001/buy-shopping-service/container/findAll")

data_containers = response.json()

#%%
containers_all = [Container(data) for data in data_containers]

allocation_all = [Allocation(data, containers_all) for data in data_allocation]

#%% extracting

retJSON = retjson(allocation_all)
print(retJSON)
