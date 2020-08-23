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
dc2 = pd.read_excel('demand_data.xlsx',sheet_name='DC2', skiprows = 8, usecols = 'B:L')
dc2.index = dc2['Category']
dc2.drop('Category', axis=1, inplace=True)
dc2 = dc2.transpose().fillna(0)

dc2_params = pd.read_excel('demand_data.xlsx',sheet_name='DC2', skiprows = 1, nrows= 6, usecols = 'B:D')
dc2_params.index = dc2_params['Category']
dc2_params.drop('Category', axis=1, inplace=True)
dc2_params = dc2_params.transpose().fillna(0)

#%% Calculation
dc2['Total Demand'] = dc2['Spot Forecast Demand(MT)'] +\
                    dc2['Spot Order (MT)'] +\
                    dc2['Term Forecast Demand (MT)'] +\
                    dc2['Term Order (MT)']

# Setting Projected Inventory and it's initial value
dc2['Proj End Inv'] = 0
dc2['Net Requirements'] = 0
dc2['Planned Receipts (MT)'] = 0
dc2['Planned Orders (MT)'] = 0
dc2['Num of 10T Trucks'] = 0
dc2['Num of 20T Trucks'] = 0
dc2['Total Transportation Cost (RM)'] = 0
dc2['Product Cost (RM)'] = 0
dc2['Total Supply Cost (RM)'] = 0
dc2['Revenue'] = 0
dc2['Profit'] = 0

first_week = dc2.index[0]
dc2.loc[first_week,'Proj End Inv'] = dc2_params.loc['Value','Initial Ending Inventory (MT)'] +\
                                    dc2.loc[first_week,'Scheduled Receipts (MT)'] +\
                                    dc2.loc[first_week,'Planned Receipts (MT)'] -\
                                    dc2.loc[first_week,'Total Demand']

PEI = dc2.columns.get_loc('Proj End Inv')
PR = dc2.columns.get_loc('Planned Receipts (MT)')
SR = dc2.columns.get_loc('Scheduled Receipts (MT)')
NR = dc2.columns.get_loc('Net Requirements')
TD = dc2.columns.get_loc('Total Demand')
PO = dc2.columns.get_loc('Planned Orders (MT)')
n10T = dc2.columns.get_loc('Num of 10T Trucks')
n20T = dc2.columns.get_loc('Num of 20T Trucks')
TTC = dc2.columns.get_loc('Total Transportation Cost (RM)')
PUC = dc2.columns.get_loc('Product Unit Cost (RM/MT)')
PC = dc2.columns.get_loc('Product Cost (RM)')
TSC = dc2.columns.get_loc('Total Supply Cost (RM)')
REV = dc2.columns.get_loc('Revenue')
PF = dc2.columns.get_loc('Profit')
PSP = dc2.columns.get_loc('Product Selling Price (RM/MT)')

SS = dc2_params.columns.get_loc('Safety Stock (MT)')
LT = dc2_params.columns.get_loc('Lead Time (weeks)')
LS = dc2_params.columns.get_loc('Lot Size (MT)')
SC10T = dc2_params.columns.get_loc('Shipment cost (10 Ton)')
SC20T = dc2_params.columns.get_loc('Shipment cost (20 Ton)')

for i in range(1, len(dc2)):
    # print(i)
    if dc2.iloc[i-1, PEI] - dc2.iloc[i, TD] <= dc2_params.iloc[0, SS]:
        dc2.iloc[i, NR] = dc2.iloc[i, TD] - dc2.iloc[i-1, PEI] + dc2_params.iloc[0, SS]
    else:
        dc2.iloc[i, NR] = 0
    
    if i >= dc2_params.iloc[0, LT]:
        dc2.iloc[i, PR] = math.ceil(dc2.iloc[i, NR]/dc2_params.iloc[0, LS])*dc2_params.iloc[0, LS]
        
    dc2.iloc[i, PEI] = dc2.iloc[i-1, PEI] + dc2.iloc[i, SR] + dc2.iloc[i, PR] - dc2.iloc[i, TD]

for i in range(0, len(dc2)-int(dc2_params.iloc[0, LT])):
    dc2.iloc[i, PO] = dc2.iloc[i + int(dc2_params.iloc[0, LT]), PR]
    
    # Adding truck count
    dc2.iloc[i, n10T] = ((dc2.iloc[i, PO] + dc2_params.iloc[0, SC10T] - 1)%dc2_params.iloc[0, SC20T])//dc2_params.iloc[0, SC10T]
    dc2.iloc[i, n20T] = (dc2.iloc[i, PO] + dc2_params.iloc[0, SC10T] - 1)//dc2_params.iloc[0, SC20T]
    
    dc2.iloc[i, TTC] = dc2.iloc[i, n10T]*dc2_params.iloc[1, SC10T] + dc2.iloc[i, n20T]*dc2_params.iloc[1, SC20T]
    dc2.iloc[i, PC] = dc2.iloc[i, PUC]*dc2.iloc[i, PO]
    dc2.iloc[i, TSC] = dc2.iloc[i, TTC] + dc2.iloc[i, PC]
    dc2.iloc[i, REV] = dc2.iloc[i, PSP]*dc2.iloc[i, PO]
    dc2.iloc[i, PF] = dc2.iloc[i, REV] - dc2.iloc[i, TSC]
    
#%% Demand Centre 3

#% Import input data
dc3 = pd.read_excel('demand_data.xlsx',sheet_name='DC3', skiprows = 8, usecols = 'B:L')
dc3.index = dc3['Category']
dc3.drop('Category', axis=1, inplace=True)
dc3 = dc3.transpose().fillna(0)

dc3_params = pd.read_excel('demand_data.xlsx',sheet_name='DC3', skiprows = 1, nrows= 6, usecols = 'B:D')
dc3_params.index = dc3_params['Category']
dc3_params.drop('Category', axis=1, inplace=True)
dc3_params = dc3_params.transpose().fillna(0)

#%% Calculation
dc3['Total Demand'] = dc3['Spot Forecast Demand(MT)'] +\
                    dc3['Spot Order (MT)'] +\
                    dc3['Term Forecast Demand (MT)'] +\
                    dc3['Term Order (MT)']

# Setting Projected Inventory and it's initial value
dc3['Proj End Inv'] = 0
dc3['Net Requirements'] = 0
dc3['Planned Receipts (MT)'] = 0
dc3['Planned Orders (MT)'] = 0
dc3['Num of 10T Trucks'] = 0
dc3['Num of 20T Trucks'] = 0
dc3['Total Transportation Cost (RM)'] = 0
dc3['Product Cost (RM)'] = 0
dc3['Total Supply Cost (RM)'] = 0
dc3['Revenue'] = 0
dc3['Profit'] = 0

first_week = dc3.index[0]
dc3.loc[first_week,'Proj End Inv'] = dc3_params.loc['Value','Initial Ending Inventory (MT)'] +\
                                    dc3.loc[first_week,'Scheduled Receipts (MT)'] +\
                                    dc3.loc[first_week,'Planned Receipts (MT)'] -\
                                    dc3.loc[first_week,'Total Demand']

PEI = dc3.columns.get_loc('Proj End Inv')
PR = dc3.columns.get_loc('Planned Receipts (MT)')
SR = dc3.columns.get_loc('Scheduled Receipts (MT)')
NR = dc3.columns.get_loc('Net Requirements')
TD = dc3.columns.get_loc('Total Demand')
PO = dc3.columns.get_loc('Planned Orders (MT)')
n10T = dc3.columns.get_loc('Num of 10T Trucks')
n20T = dc3.columns.get_loc('Num of 20T Trucks')
TTC = dc3.columns.get_loc('Total Transportation Cost (RM)')
PUC = dc3.columns.get_loc('Product Unit Cost (RM/MT)')
PC = dc3.columns.get_loc('Product Cost (RM)')
TSC = dc3.columns.get_loc('Total Supply Cost (RM)')
REV = dc3.columns.get_loc('Revenue')
PF = dc3.columns.get_loc('Profit')
PSP = dc3.columns.get_loc('Product Selling Price (RM/MT)')

SS = dc3_params.columns.get_loc('Safety Stock (MT)')
LT = dc3_params.columns.get_loc('Lead Time (weeks)')
LS = dc3_params.columns.get_loc('Lot Size (MT)')
SC10T = dc3_params.columns.get_loc('Shipment cost (10 Ton)')
SC20T = dc3_params.columns.get_loc('Shipment cost (20 Ton)')

for i in range(1, len(dc3)):
    # print(i)
    if dc3.iloc[i-1, PEI] - dc3.iloc[i, TD] <= dc3_params.iloc[0, SS]:
        dc3.iloc[i, NR] = dc3.iloc[i, TD] - dc3.iloc[i-1, PEI] + dc3_params.iloc[0, SS]
    else:
        dc3.iloc[i, NR] = 0
    
    if i >= dc3_params.iloc[0, LT]:
        dc3.iloc[i, PR] = math.ceil(dc3.iloc[i, NR]/dc3_params.iloc[0, LS])*dc3_params.iloc[0, LS]
        
    dc3.iloc[i, PEI] = dc3.iloc[i-1, PEI] + dc3.iloc[i, SR] + dc3.iloc[i, PR] - dc3.iloc[i, TD]

for i in range(0, len(dc3)-int(dc3_params.iloc[0, LT])):
    dc3.iloc[i, PO] = dc3.iloc[i + int(dc3_params.iloc[0, LT]), PR]
    
    # Adding truck count
    dc3.iloc[i, n10T] = ((dc3.iloc[i, PO] + dc3_params.iloc[0, SC10T] - 1)%dc3_params.iloc[0, SC20T])//dc3_params.iloc[0, SC10T]
    dc3.iloc[i, n20T] = (dc3.iloc[i, PO] + dc3_params.iloc[0, SC10T] - 1)//dc3_params.iloc[0, SC20T]
    
    dc3.iloc[i, TTC] = dc3.iloc[i, n10T]*dc3_params.iloc[1, SC10T] + dc3.iloc[i, n20T]*dc3_params.iloc[1, SC20T]
    dc3.iloc[i, PC] = dc3.iloc[i, PUC]*dc3.iloc[i, PO]
    dc3.iloc[i, TSC] = dc3.iloc[i, TTC] + dc3.iloc[i, PC]
    dc3.iloc[i, REV] = dc3.iloc[i, PSP]*dc3.iloc[i, PO]
    dc3.iloc[i, PF] = dc3.iloc[i, REV] - dc3.iloc[i, TSC]