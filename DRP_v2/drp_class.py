# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 18:16:41 2020

@author: James Ang
"""


#% Set Directory
import os
os.chdir(r'C:/Users/User/Documents/ghub_acceval/smarttradzt-python-services/DRP_v2/')

#%%
import copy
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 200)

from IPython.display import display
from drp_lib import Demand_Centre, Demand_Centre_Params, Supplier, Supplier_Params, Optimize_DRP, print_out


#%% Import Data
excelfilename = 'input_data.xlsx'

# DC1 Input Data
dc1 = Demand_Centre(excelfilename, 'DC1')

# DC1 Input Parameters
dc1_params = Demand_Centre_Params(excelfilename, 'DC1')

#%% DC2 Input Data
dc2 = Demand_Centre(excelfilename, 'DC2')

# DC2 Input Parameters
dc2_params = Demand_Centre_Params(excelfilename, 'DC2')

#%% DC3 Input Data
dc3 = Demand_Centre(excelfilename, 'DC3')

# DC3 Input Parameters
dc3_params = Demand_Centre_Params(excelfilename, 'DC3')

#%% All
dc_all = [dc1,dc2,dc3]

dc_params_all = [dc1_params, dc2_params, dc3_params]

#%% Supplier Input Data
number_of_suppliers = 2
supp_params_all = []

# Supplier 1 Input Parameters
for i in range(1, number_of_suppliers+1):
    
    supp_params_all.append(Supplier_Params(excelfilename, f'Supplier{i}'))

# supp1_params = Supplier_Params(excelfilename, 'Supplier1')

# # Supplier 2 Input Parameters
# supp2_params = Supplier_Params(excelfilename, 'Supplier2')

# supp_params_all = [supp1_params, supp2_params]

if all(supp.supplier_availability == 'No' for supp in supp_params_all):
    
    print("All Suppliers are not available.")

else:
    
    #%% Demand Centre 1
    
    # Calculate
    dc1.calculate(supp_params_all, dc1_params)
    
    # dc1_test.calculate(supp_params_all, dc1_params)
    
    # Copy
    dc1_ori = copy.deepcopy(dc1)
    
    #%% Demand Centre 2
    
    # Calculate
    dc2.calculate(supp_params_all, dc2_params)
    
    # Copy
    dc2_ori = copy.deepcopy(dc2)
    
    #%% Demand Centre 3
    
    # Calculate
    dc3.calculate(supp_params_all, dc3_params)
    
    # Copy
    dc3_ori = copy.deepcopy(dc3)
    
    #%% Supplier 1
    
    supp_ori = []
    
    for i in range(0,number_of_suppliers):
    # Supplier 1
        supp_ori.append(Supplier(supp_params_all[i], f'Supplier {i+1}', dc_all))
        #supp1_ori = Supplier(supp1_params, 'Supplier 1', dc_all)
        supp_ori[i].calculate(supp_params_all[i], dc_all, dc_params_all)
    # Calculate
    # supp1_ori.calculate(supp1_params, dc_all, dc_params_all)
    
    # #%% Supplier 2
    
    # # Supplier 2
    # supp2_ori = Supplier(supp2_params, 'Supplier 2', dc_all)
    
    # # Calculate
    # supp2_ori.calculate(supp2_params, dc_all, dc_params_all)
    
    

    
    #%% Optimisation
    
    supp_opt = []
    
    for i in range(0,number_of_suppliers):
        
        supp_opt.append(Optimize_DRP(supp_params_all[i], f'Supplier {i+1}', dc_all))
    
        supp_opt[i].optimize(supp_params_all[i], dc_all, dc_params_all)
        
        # If "Quantity to Reduce" still not 0, then optimize again
        while any(supp_opt[i].qty_to_reduce != 0):
            supp_opt[i].optimize(supp_params_all[i], dc_all, dc_params_all)
        

#%% Print results
# for dc in dc_all:
#     print(dc.planned_orders)

# dc1_ori_df = print_out(dc1_ori)
# dc2_ori_df = print_out(dc2_ori)
# dc3_ori_df = print_out(dc3_ori)

# dc1_df = print_out(dc1)
# dc2_df = print_out(dc2)
# dc3_df = print_out(dc3)

# display(dc1_ori_df)
# display(dc1_df)

# display(dc2_ori_df)
# display(dc2_df)

# display(dc3_ori_df)
# display(dc3_df)
