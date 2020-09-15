# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 18:16:41 2020

@author: James Ang
"""
import copy
from drp_lib import Demand_Centre, Demand_Centre_Params

excelfilename = 'demand_data.xlsx'

#%% Demand Centre 1

# Input Data
dc1 = Demand_Centre(excelfilename, 'DC1')

# Parameters
dc1_params = Demand_Centre_Params(excelfilename, 'DC1')

# Calculate
dc1.calculate(dc1_params)

# Copy
dc1_ori = copy.deepcopy(dc1)

#%% Demand Centre 2

# Input Data
dc2 = Demand_Centre(excelfilename, 'DC2')

# Parameters
dc2_params = Demand_Centre_Params(excelfilename, 'DC2')

# Calculate
dc2.calculate(dc2_params)

# Copy
dc2_ori = copy.deepcopy(dc2)

#%% Demand Centre 3

# Input Data
dc3 = Demand_Centre(excelfilename, 'DC3')

# Parameters
dc3_params = Demand_Centre_Params(excelfilename, 'DC3')

# Calculate
dc3.calculate(dc3_params)

# Copy
dc3_ori = copy.deepcopy(dc3)

