# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 14:52:26 2020

@author: James Ang
"""

import pandas as pd
import os
import math

#% Set Directory
os.chdir(r'C:/Users/User/Documents/ghub_acceval/smarttradzt-python-services/DRP/')

#%% Import input data

dc1 = pd.read_excel('demand_data.xlsx',sheet_name='DC1', skiprows = 8, usecols = 'B:L')
dc1.index = dc1['Category']
dc1.drop('Category', axis=1, inplace=True)
dc1 = dc1.transpose().fillna(0)

# Index(['Spot Forecast Demand(MT)', 'Spot Order (MT)',
#        'Term Forecast Demand (MT)', 'Term Order (MT)',
#        'Scheduled Receipts (MT)', 'Product Unit Cost (RM/MT)',
#        'Product Selling Price (RM/MT)']

dc1_params = pd.read_excel('demand_data.xlsx',sheet_name='DC1', skiprows = 1, nrows= 6, usecols = 'B:D')
dc1_params.index = dc1_params['Category']
dc1_params.drop('Category', axis=1, inplace=True)
dc1_params = dc1_params.transpose().fillna(0)

#%% Calculation
dc1['Total Demand'] = dc1['Spot Forecast Demand(MT)'] +\
                    dc1['Spot Order (MT)'] +\
                    dc1['Term Forecast Demand (MT)'] +\
                    dc1['Term Order (MT)']

# Setting Projected Inventory and it's initial value
dc1['Proj End Inv'] = 0
dc1['Net Requirements'] = 0
dc1['Planned Receipts (MT)'] = 0
dc1['Planned Orders (MT)'] = 0
dc1['Num of 10T Trucks'] = 0
dc1['Num of 20T Trucks'] = 0
dc1['Total Transportation Cost (RM)'] = 0
dc1['Product Cost (RM)'] = 0
dc1['Total Supply Cost (RM)'] = 0
dc1['Revenue'] = 0
dc1['Profit'] = 0

first_week = dc1.index[0]
dc1.loc[first_week,'Proj End Inv'] = dc1_params.loc['Value','Initial Ending Inventory (MT)'] +\
                                    dc1.loc[first_week,'Scheduled Receipts (MT)'] +\
                                    dc1.loc[first_week,'Planned Receipts (MT)'] -\
                                    dc1.loc[first_week,'Total Demand']

PEI = dc1.columns.get_loc('Proj End Inv')
PR = dc1.columns.get_loc('Planned Receipts (MT)')
SR = dc1.columns.get_loc('Scheduled Receipts (MT)')
NR = dc1.columns.get_loc('Net Requirements')
TD = dc1.columns.get_loc('Total Demand')
PO = dc1.columns.get_loc('Planned Orders (MT)')
n10T = dc1.columns.get_loc('Num of 10T Trucks')
n20T = dc1.columns.get_loc('Num of 20T Trucks')
TTC = dc1.columns.get_loc('Total Transportation Cost (RM)')
PUC = dc1.columns.get_loc('Product Unit Cost (RM/MT)')
PC = dc1.columns.get_loc('Product Cost (RM)')
TSC = dc1.columns.get_loc('Total Supply Cost (RM)')
REV = dc1.columns.get_loc('Revenue')
PF = dc1.columns.get_loc('Profit')
PSP = dc1.columns.get_loc('Product Selling Price (RM/MT)')

SS = dc1_params.columns.get_loc('Safety Stock (MT)')
LT = dc1_params.columns.get_loc('Lead Time (weeks)')
LS = dc1_params.columns.get_loc('Lot Size (MT)')
SC10T = dc1_params.columns.get_loc('Shipment cost (10 Ton)')
SC20T = dc1_params.columns.get_loc('Shipment cost (20 Ton)')

for i in range(1, len(dc1)):
    # print(i)
    if dc1.iloc[i-1, PEI] - dc1.iloc[i, TD] <= dc1_params.iloc[0, SS]:
        dc1.iloc[i, NR] = dc1.iloc[i, TD] - dc1.iloc[i-1, PEI] + dc1_params.iloc[0, SS]
    else:
        dc1.iloc[i, NR] = 0
    
    if i >= dc1_params.iloc[0, LT]:
        dc1.iloc[i, PR] = math.ceil(dc1.iloc[i, NR]/dc1_params.iloc[0, LS])*dc1_params.iloc[0, LS]
        
    dc1.iloc[i, PEI] = dc1.iloc[i-1, PEI] + dc1.iloc[i, SR] + dc1.iloc[i, PR] - dc1.iloc[i, TD]

for i in range(0, len(dc1)-int(dc1_params.iloc[0, LT])):
    dc1.iloc[i, PO] = dc1.iloc[i + int(dc1_params.iloc[0, LT]), PR]
    
    # Adding truck count
    dc1.iloc[i, n10T] = ((dc1.iloc[i, PO] + dc1_params.iloc[0, SC10T] - 1)%dc1_params.iloc[0, SC20T])//dc1_params.iloc[0, SC10T]
    dc1.iloc[i, n20T] = (dc1.iloc[i, PO] + dc1_params.iloc[0, SC10T] - 1)//dc1_params.iloc[0, SC20T]
    
    dc1.iloc[i, TTC] = dc1.iloc[i, n10T]*dc1_params.iloc[1, SC10T] + dc1.iloc[i, n20T]*dc1_params.iloc[1, SC20T]
    dc1.iloc[i, PC] = dc1.iloc[i, PUC]*dc1.iloc[i, PO]
    dc1.iloc[i, TSC] = dc1.iloc[i, TTC] + dc1.iloc[i, PC]
    dc1.iloc[i, REV] = dc1.iloc[i, PSP]*dc1.iloc[i, PO]
    dc1.iloc[i, PF] = dc1.iloc[i, REV] - dc1.iloc[i, TSC]
    
#%% Demand Centre 2

#% Import input data
# dc1 = pd.read_excel('demand_data.xlsx',sheet_name='DC1', skiprows = 8, usecols = 'B:L')
# dc1.index = dc1['Category']
# dc1.drop('Category', axis=1, inplace=True)
# dc1 = dc1.transpose().fillna(0)
