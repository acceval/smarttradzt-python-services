# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 18:16:41 2020

@author: James Ang
"""

import os
import copy
from drp_lib import Demand_Centre, Demand_Centre_Params, Supplier, Supplier_Params, Optimize_DRP


#% Set Directory
os.chdir(r'C:/Users/User/Documents/ghub_acceval/smarttradzt-python-services/DRP/')

excelfilename = 'demand_data_2suppliers.xlsx'

#% Import Data

# DC1 Input Data
dc1 = Demand_Centre(excelfilename, 'DC1')

# DC1 Input Parameters
dc1_params = Demand_Centre_Params(excelfilename, 'DC1')

# DC2 Input Data
dc2 = Demand_Centre(excelfilename, 'DC2')

# DC2 Input Parameters
dc2_params = Demand_Centre_Params(excelfilename, 'DC2')

# DC3 Input Data
dc3 = Demand_Centre(excelfilename, 'DC3')

# DC3 Input Parameters
dc3_params = Demand_Centre_Params(excelfilename, 'DC3')

# Supplier 1 Input Parameters
supp1_params = Supplier_Params(excelfilename, 'Supplier1')

# Supplier 2 Input Parameters
supp2_params = Supplier_Params(excelfilename, 'Supplier2')

#%% Demand Centre 1

# Calculate
dc1.calculate([supp1_params, supp2_params], dc1_params)

# Copy
dc1_ori = copy.deepcopy(dc1)

#%% Demand Centre 2

# Calculate
dc2.calculate([supp1_params, supp2_params], dc2_params)

# Copy
dc2_ori = copy.deepcopy(dc2)

#%% Demand Centre 3

# Calculate
dc3.calculate([supp1_params, supp2_params], dc3_params)

# Copy
dc3_ori = copy.deepcopy(dc3)

#%% Supplier 1

# Supplier 1
supp1 = Supplier(supp1_params,'Supplier 1', [dc1,dc2,dc3])

# Calculate
supp1.calculate(supp1_params)

# Make a Copy
supp1_ori = copy.deepcopy(supp1)

#%% Supplier 2

# Supplier 2
supp2 = Supplier(supp2_params,'Supplier 2', [dc1,dc2,dc3])

# Calculate
supp2.calculate(supp2_params)

# Make a Copy
supp2_ori = copy.deepcopy(supp2)

#%% Optimisation
optimized = Optimize_DRP(supp1,[dc1,dc2,dc3])
