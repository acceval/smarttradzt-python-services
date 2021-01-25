# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 13:36:35 2021

@author: James Ang
"""


import json
from alloc_plan_lib import Supplier_Alloc, Weight_Score, Calc_Month

# Opening JSON file
f = open('input_alloc_plan2.json',)

data = json.load(f)

data_basic = data.get('basic_data')

data_vacc_alloc = data.get('vaccine_allocation')

data_weight_score = data.get('weighted_scores')

data_supp_month_alloc = data.get('supplier_monthly_alloc')

#%%

weighted_scores_all = [Weight_Score(data) for data in data_weight_score]

supp_alloc_all = [Supplier_Alloc(data) for data in data_supp_month_alloc]

#%%

calculated = Calc_Month(data_basic, data_vacc_alloc, data_supp_month_alloc)

