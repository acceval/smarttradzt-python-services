# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 11:51:03 2020

@author: James Ang
"""

#% Set Directory
import os
os.chdir(r'C:/Users/User/Documents/ghub_acceval/smarttradzt-python-services/SDBal/')

#%% Import libraries
import pandas as pd
from sdbal_lib import Month_Demand, Month_Order, Gen_Supp_Plan

#%% Import Data
excelfilename = 'input_data.xlsx'

# Demand
monthdemand_m = Month_Demand(excelfilename, 'rank_sept')
monthdemand_m1 = Month_Demand(excelfilename, 'rank_oct')
monthdemand_m2 = Month_Demand(excelfilename, 'rank_nov')
monthdemand_m3 = Month_Demand(excelfilename, 'rank_dec')

monthorder_m0 = Month_Order(excelfilename, 'rank_sept')
monthorder_m1 = Month_Order(excelfilename, 'rank_oct')
monthorder_m2 = Month_Order(excelfilename, 'rank_nov')
monthorder_m3 = Month_Order(excelfilename, 'rank_dec')

# Demand plan month m-1
threemonths_demand_m_minus_1 = [monthdemand_m, monthdemand_m1, monthdemand_m2]
threemonths_demand_forecast = [month.totaldemand for month in threemonths_demand_m_minus_1]

# prod_qty_m = 2350     # Supply plan month m (Sept)
prod_qty_m = pd.read_excel(excelfilename, sheet_name='S&DBalancing', skiprows = 24, nrows = 1, usecols = 'L').iloc[0,0]
prod_qty = prod_qty_m

# maximum_production_limit = 2400
maximum_production_limit = pd.read_excel(excelfilename, sheet_name='S&DBalancing', skiprows = 8, nrows = 1, usecols = 'D').iloc[0,0]

# ini_end_inv_m_minus_1 = 450
ini_end_inv_m_minus_1 = pd.read_excel(excelfilename, sheet_name='S&DBalancing', skiprows = 26, nrows = 1, usecols = 'K').iloc[0,0]
ini_end_inv = ini_end_inv_m_minus_1

# target_ending_inventory = [250, 300, 260]
target_ending_inventory = pd.read_excel(excelfilename, sheet_name='S&DBalancing', skiprows = 27, nrows = 1, usecols = 'L:N').iloc[0,:].to_list()

# final_month_end_total_order_m = 2650  # Manual Entry
final_month_end_total_order_m = pd.read_excel(excelfilename, sheet_name='S&DBalancing', skiprows = 23, nrows = 1, usecols = 'L').iloc[0,0]
final_month_end_total_order = final_month_end_total_order_m

# Supply plan month m-1
print('\nCalculating month m-1...')
supp_plan_m_minus_1 = Gen_Supp_Plan(excelfilename, 'S&DBalancing', threemonths_demand_forecast, prod_qty, ini_end_inv, final_month_end_total_order, maximum_production_limit, target_ending_inventory)

#%% simulate month

# Demand plan month m
threemonths_demand_m = [monthdemand_m1, monthdemand_m2, monthdemand_m3]
# threemonths_demand_forecast = [month.totaldemand for month in threemonths_demand_m]
threemonths_demand_forecast = [2365, 3200, 2285]

# Supply plan month m-1
prod_qty = supp_plan_m_minus_1.supply_plan_next_month

ini_end_inv = supp_plan_m_minus_1.initial_end_inv_next_month

# target_ending_inventory = [250, 300, 260]
target_ending_inventory = pd.read_excel(excelfilename, sheet_name='S&DBalancing2', skiprows = 27, nrows = 1, usecols = 'L:N').iloc[0,:].to_list()

# final_month_end_total_order_m = 2000
final_month_end_total_order_m = pd.read_excel(excelfilename, sheet_name='S&DBalancing2', skiprows = 23, nrows = 1, usecols = 'L').iloc[0,0]
final_month_end_total_order = final_month_end_total_order_m

print('\nCalculating month m...')
supp_plan_m = Gen_Supp_Plan(excelfilename, 'S&DBalancing', threemonths_demand_forecast, prod_qty, ini_end_inv, final_month_end_total_order, maximum_production_limit, target_ending_inventory)
