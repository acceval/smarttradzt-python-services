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
dc1['Spot Demand'] = 0
dc1['Spot Demand to Reduce'] = 0
dc1['Spot - Num of 10T Trucks'] = 0
dc1['Spot - Num of 20T Trucks'] = 0
dc1['Spot Transportation Cost (RM)'] = 0
dc1['Spot Product Cost (RM)'] = 0
dc1['Spot Supply Cost (RM)'] = 0
dc1['Spot Revenue'] = 0
dc1['Spot Profit'] = 0
dc1['Updated Spot Forecast Demand'] = 0

first_week = dc1.index[0]
dc1.loc[first_week,'Proj End Inv'] = dc1_params.loc['Value','Initial Ending Inventory (MT)'] +\
                                    dc1.loc[first_week,'Scheduled Receipts (MT)'] +\
                                    dc1.loc[first_week,'Planned Receipts (MT)'] -\
                                    dc1.loc[first_week,'Total Demand']

PEI_1 = dc1.columns.get_loc('Proj End Inv')
PR_1 = dc1.columns.get_loc('Planned Receipts (MT)')
SR_1 = dc1.columns.get_loc('Scheduled Receipts (MT)')
NR_1 = dc1.columns.get_loc('Net Requirements')
TD_1 = dc1.columns.get_loc('Total Demand')
PO_1 = dc1.columns.get_loc('Planned Orders (MT)')
n10T_1 = dc1.columns.get_loc('Num of 10T Trucks')
n20T_1 = dc1.columns.get_loc('Num of 20T Trucks')
TTC_1 = dc1.columns.get_loc('Total Transportation Cost (RM)')
PUC_1 = dc1.columns.get_loc('Product Unit Cost (RM/MT)')
PC_1 = dc1.columns.get_loc('Product Cost (RM)')
TSC_1 = dc1.columns.get_loc('Total Supply Cost (RM)')
REV_1 = dc1.columns.get_loc('Revenue')
PF_1 = dc1.columns.get_loc('Profit')
PSP_1 = dc1.columns.get_loc('Product Selling Price (RM/MT)')
SFD_1 = dc1.columns.get_loc('Spot Forecast Demand(MT)')
SO_1 = dc1.columns.get_loc('Spot Order (MT)')
SD_1 = dc1.columns.get_loc('Spot Demand')
SDTR_1 = dc1.columns.get_loc('Spot Demand to Reduce')
Sn10T_1 = dc1.columns.get_loc('Spot - Num of 10T Trucks')
Sn20T_1 = dc1.columns.get_loc('Spot - Num of 20T Trucks')
STC_1 = dc1.columns.get_loc('Spot Transportation Cost (RM)')
SPC_1 = dc1.columns.get_loc('Spot Product Cost (RM)')
SSC_1 = dc1.columns.get_loc('Spot Supply Cost (RM)')
SRev_1 = dc1.columns.get_loc('Spot Revenue')
SP_1 = dc1.columns.get_loc('Spot Profit')
USFD_1 = dc1.columns.get_loc('Updated Spot Forecast Demand')

SS_1 = dc1_params.columns.get_loc('Safety Stock (MT)')
LT_1 = dc1_params.columns.get_loc('Lead Time (weeks)')
LS_1 = dc1_params.columns.get_loc('Lot Size (MT)')
SC10T_1 = dc1_params.columns.get_loc('Shipment cost (10 Ton)')
SC20T_1 = dc1_params.columns.get_loc('Shipment cost (20 Ton)')

for i in range(1, len(dc1)):
    # Net Requirements
    if dc1.iloc[i-1, PEI_1] - dc1.iloc[i, TD_1] <= dc1_params.iloc[0, SS_1]:
        dc1.iloc[i, NR_1] = dc1.iloc[i, TD_1] - dc1.iloc[i-1, PEI_1] + dc1_params.iloc[0, SS_1]
    else:
        dc1.iloc[i, NR_1] = 0
    
    # Planned Receipts
    if i >= dc1_params.iloc[0, LT_1]:
        dc1.iloc[i, PR_1] = math.ceil(dc1.iloc[i, NR_1]/dc1_params.iloc[0, LS_1])*dc1_params.iloc[0, LS_1]
    
    # Projected Ending Inventory
    dc1.iloc[i, PEI_1] = dc1.iloc[i-1, PEI_1] + dc1.iloc[i, SR_1] + dc1.iloc[i, PR_1] - dc1.iloc[i, TD_1]

for i in range(0, len(dc1)-int(dc1_params.iloc[0, LT_1])):
    
    # Planned Orders
    dc1.iloc[i, PO_1] = dc1.iloc[i + int(dc1_params.iloc[0, LT_1]), PR_1]
    
    # Adding truck count
    dc1.iloc[i, n10T_1] = ((dc1.iloc[i, PO_1] + dc1_params.iloc[0, SC10T_1] - 1)%dc1_params.iloc[0, SC20T_1])//dc1_params.iloc[0, SC10T_1]
    dc1.iloc[i, n20T_1] = (dc1.iloc[i, PO_1] + dc1_params.iloc[0, SC10T_1] - 1)//dc1_params.iloc[0, SC20T_1]
    
    # Total Transportation Cost
    dc1.iloc[i, TTC_1] = dc1.iloc[i, n10T_1]*dc1_params.iloc[1, SC10T_1] + dc1.iloc[i, n20T_1]*dc1_params.iloc[1, SC20T_1]
    
    # Product Cost
    dc1.iloc[i, PC_1] = dc1.iloc[i, PUC_1]*dc1.iloc[i, PO_1]
    
    # Total Supply Cost
    dc1.iloc[i, TSC_1] = dc1.iloc[i, TTC_1] + dc1.iloc[i, PC_1]
    
    # Revenue
    dc1.iloc[i, REV_1] = dc1.iloc[i, PSP_1]*dc1.iloc[i, PO_1]
    
    # Profit
    dc1.iloc[i, PF_1] = dc1.iloc[i, REV_1] - dc1.iloc[i, TSC_1]
    
    # Spot Demand
    dc1.iloc[i, SD_1] = dc1.iloc[i + int(dc1_params.iloc[0, LT_1]), SFD_1] + dc1.iloc[i + int(dc1_params.iloc[0, LT_1]), SO_1]

dc1['Updated Spot Forecast Demand'] = dc1['Spot Forecast Demand(MT)']
    
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
dc2['Spot Demand'] = 0
dc2['Spot Demand to Reduce'] = 0
dc2['Spot - Num of 10T Trucks'] = 0
dc2['Spot - Num of 20T Trucks'] = 0
dc2['Spot Transportation Cost (RM)'] = 0
dc2['Spot Product Cost (RM)'] = 0
dc2['Spot Supply Cost (RM)'] = 0
dc2['Spot Revenue'] = 0
dc2['Spot Profit'] = 0
dc2['Updated Spot Forecast Demand'] = 0

first_week = dc2.index[0]
dc2.loc[first_week,'Proj End Inv'] = dc2_params.loc['Value','Initial Ending Inventory (MT)'] +\
                                    dc2.loc[first_week,'Scheduled Receipts (MT)'] +\
                                    dc2.loc[first_week,'Planned Receipts (MT)'] -\
                                    dc2.loc[first_week,'Total Demand']
PEI_2 = dc2.columns.get_loc('Proj End Inv')
PR_2 = dc2.columns.get_loc('Planned Receipts (MT)')
SR_2 = dc2.columns.get_loc('Scheduled Receipts (MT)')
NR_2 = dc2.columns.get_loc('Net Requirements')
TD_2 = dc2.columns.get_loc('Total Demand')
PO_2 = dc2.columns.get_loc('Planned Orders (MT)')
n10T_2 = dc2.columns.get_loc('Num of 10T Trucks')
n20T_2 = dc2.columns.get_loc('Num of 20T Trucks')
TTC_2 = dc2.columns.get_loc('Total Transportation Cost (RM)')
PUC_2 = dc2.columns.get_loc('Product Unit Cost (RM/MT)')
PC_2 = dc2.columns.get_loc('Product Cost (RM)')
TSC_2 = dc2.columns.get_loc('Total Supply Cost (RM)')
REV_2 = dc2.columns.get_loc('Revenue')
PF_2 = dc2.columns.get_loc('Profit')
PSP_2 = dc2.columns.get_loc('Product Selling Price (RM/MT)')
SFD_2 = dc2.columns.get_loc('Spot Forecast Demand(MT)')
SO_2 = dc2.columns.get_loc('Spot Order (MT)')
SD_2 = dc2.columns.get_loc('Spot Demand')
SDTR_2 = dc2.columns.get_loc('Spot Demand to Reduce')
Sn10T_2 = dc2.columns.get_loc('Spot - Num of 10T Trucks')
Sn20T_2 = dc2.columns.get_loc('Spot - Num of 20T Trucks')
STC_2 = dc2.columns.get_loc('Spot Transportation Cost (RM)')
SPC_2 = dc2.columns.get_loc('Spot Product Cost (RM)')
SSC_2 = dc2.columns.get_loc('Spot Supply Cost (RM)')
SRev_2 = dc2.columns.get_loc('Spot Revenue')
SP_2 = dc2.columns.get_loc('Spot Profit')
USFD_2 = dc2.columns.get_loc('Updated Spot Forecast Demand')

SS_2 = dc2_params.columns.get_loc('Safety Stock (MT)')
LT_2 = dc2_params.columns.get_loc('Lead Time (weeks)')
LS_2 = dc2_params.columns.get_loc('Lot Size (MT)')
SC10T_2 = dc2_params.columns.get_loc('Shipment cost (10 Ton)')
SC20T_2 = dc2_params.columns.get_loc('Shipment cost (20 Ton)')

for i in range(1, len(dc2)):
    # Net Requirements
    if dc2.iloc[i-1, PEI_2] - dc2.iloc[i, TD_2] <= dc2_params.iloc[0, SS_2]:
        dc2.iloc[i, NR_2] = dc2.iloc[i, TD_2] - dc2.iloc[i-1, PEI_2] + dc2_params.iloc[0, SS_2]
    else:
        dc2.iloc[i, NR_2] = 0
    
    # Planned Receipts
    if i >= dc2_params.iloc[0, LT_2]:
        dc2.iloc[i, PR_2] = math.ceil(dc2.iloc[i, NR_2]/dc2_params.iloc[0, LS_2])*dc2_params.iloc[0, LS_2]
    
    # Projected Ending Inventory
    dc2.iloc[i, PEI_2] = dc2.iloc[i-1, PEI_2] + dc2.iloc[i, SR_2] + dc2.iloc[i, PR_2] - dc2.iloc[i, TD_2]

for i in range(0, len(dc2)-int(dc2_params.iloc[0, LT_2])):
    
    # Planned Orders
    dc2.iloc[i, PO_2] = dc2.iloc[i + int(dc2_params.iloc[0, LT_2]), PR_2]
    
    # Adding truck count
    dc2.iloc[i, n10T_2] = ((dc2.iloc[i, PO_2] + dc2_params.iloc[0, SC10T_2] - 1)%dc2_params.iloc[0, SC20T_2])//dc2_params.iloc[0, SC10T_2]
    dc2.iloc[i, n20T_2] = (dc2.iloc[i, PO_2] + dc2_params.iloc[0, SC10T_2] - 1)//dc2_params.iloc[0, SC20T_2]
    
    # Total Transportation Cost
    dc2.iloc[i, TTC_2] = dc2.iloc[i, n10T_2]*dc2_params.iloc[1, SC10T_2] + dc2.iloc[i, n20T_2]*dc2_params.iloc[1, SC20T_2]
    
    # Product Cost
    dc2.iloc[i, PC_2] = dc2.iloc[i, PUC_2]*dc2.iloc[i, PO_2]
    
    # Total Supply Cost
    dc2.iloc[i, TSC_2] = dc2.iloc[i, TTC_2] + dc2.iloc[i, PC_2]
    
    # Revenue
    dc2.iloc[i, REV_2] = dc2.iloc[i, PSP_2]*dc2.iloc[i, PO_2]
    
    # Profit
    dc2.iloc[i, PF_2] = dc2.iloc[i, REV_2] - dc2.iloc[i, TSC_2]
    
    # Spot Demand
    dc2.iloc[i, SD_2] = dc2.iloc[i + int(dc2_params.iloc[0, LT_2]), SFD_2] + dc2.iloc[i + int(dc2_params.iloc[0, LT_2]), SO_2]

dc2['Updated Spot Forecast Demand'] = dc2['Spot Forecast Demand(MT)']

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

#%% Calculations
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
dc3['Spot Demand'] = 0
dc3['Spot Demand to Reduce'] = 0
dc3['Spot - Num of 10T Trucks'] = 0
dc3['Spot - Num of 20T Trucks'] = 0
dc3['Spot Transportation Cost (RM)'] = 0
dc3['Spot Product Cost (RM)'] = 0
dc3['Spot Supply Cost (RM)'] = 0
dc3['Spot Revenue'] = 0
dc3['Spot Profit'] = 0
dc3['Updated Spot Forecast Demand'] = 0

first_week = dc3.index[0]
dc3.loc[first_week,'Proj End Inv'] = dc3_params.loc['Value','Initial Ending Inventory (MT)'] +\
                                    dc3.loc[first_week,'Scheduled Receipts (MT)'] +\
                                    dc3.loc[first_week,'Planned Receipts (MT)'] -\
                                    dc3.loc[first_week,'Total Demand']

PEI_3 = dc3.columns.get_loc('Proj End Inv')
PR_3 = dc3.columns.get_loc('Planned Receipts (MT)')
SR_3 = dc3.columns.get_loc('Scheduled Receipts (MT)')
NR_3 = dc3.columns.get_loc('Net Requirements')
TD_3 = dc3.columns.get_loc('Total Demand')
PO_3 = dc3.columns.get_loc('Planned Orders (MT)')
n10T_3 = dc3.columns.get_loc('Num of 10T Trucks')
n20T_3 = dc3.columns.get_loc('Num of 20T Trucks')
TTC_3 = dc3.columns.get_loc('Total Transportation Cost (RM)')
PUC_3 = dc3.columns.get_loc('Product Unit Cost (RM/MT)')
PC_3 = dc3.columns.get_loc('Product Cost (RM)')
TSC_3 = dc3.columns.get_loc('Total Supply Cost (RM)')
REV_3 = dc3.columns.get_loc('Revenue')
PF_3 = dc3.columns.get_loc('Profit')
PSP_3 = dc3.columns.get_loc('Product Selling Price (RM/MT)')
SFD_3 = dc3.columns.get_loc('Spot Forecast Demand(MT)')
SO_3 = dc3.columns.get_loc('Spot Order (MT)')
SD_3 = dc3.columns.get_loc('Spot Demand')
SDTR_3 = dc3.columns.get_loc('Spot Demand to Reduce')
Sn10T_3 = dc3.columns.get_loc('Spot - Num of 10T Trucks')
Sn20T_3 = dc3.columns.get_loc('Spot - Num of 20T Trucks')
STC_3 = dc3.columns.get_loc('Spot Transportation Cost (RM)')
SPC_3 = dc3.columns.get_loc('Spot Product Cost (RM)')
SSC_3 = dc3.columns.get_loc('Spot Supply Cost (RM)')
SRev_3 = dc3.columns.get_loc('Spot Revenue')
SP_3 = dc3.columns.get_loc('Spot Profit')
USFD_3 = dc3.columns.get_loc('Updated Spot Forecast Demand')


SS_3 = dc3_params.columns.get_loc('Safety Stock (MT)')
LT_3 = dc3_params.columns.get_loc('Lead Time (weeks)')
LS_3 = dc3_params.columns.get_loc('Lot Size (MT)')
SC10T_3 = dc3_params.columns.get_loc('Shipment cost (10 Ton)')
SC20T_3 = dc3_params.columns.get_loc('Shipment cost (20 Ton)')

for i in range(1, len(dc3)):
    # Net Requirements
    if dc3.iloc[i-1, PEI_3] - dc3.iloc[i, TD_3] <= dc3_params.iloc[0, SS_3]:
        dc3.iloc[i, NR_3] = dc3.iloc[i, TD_3] - dc3.iloc[i-1, PEI_3] + dc3_params.iloc[0, SS_3]
    else:
        dc3.iloc[i, NR_3] = 0
    
    # Planned Receipts
    if i >= dc3_params.iloc[0, LT_3]:
        dc3.iloc[i, PR_3] = math.ceil(dc3.iloc[i, NR_3]/dc3_params.iloc[0, LS_3])*dc3_params.iloc[0, LS_3]
    
    # Projected Ending Inventory
    dc3.iloc[i, PEI_3] = dc3.iloc[i-1, PEI_3] + dc3.iloc[i, SR_3] + dc3.iloc[i, PR_3] - dc3.iloc[i, TD_3]

for i in range(0, len(dc3)-int(dc3_params.iloc[0, LT_3])):
    
    # Planned Orders
    dc3.iloc[i, PO_3] = dc3.iloc[i + int(dc3_params.iloc[0, LT_3]), PR_3]
    
    # Truck count - 10T, 20T
    dc3.iloc[i, n10T_3] = ((dc3.iloc[i, PO_3] + dc3_params.iloc[0, SC10T_3] - 1)%dc3_params.iloc[0, SC20T_3])//dc3_params.iloc[0, SC10T_3]
    dc3.iloc[i, n20T_3] = (dc3.iloc[i, PO_3] + dc3_params.iloc[0, SC10T_3] - 1)//dc3_params.iloc[0, SC20T_3]
    
    # Total Transportation Cost
    dc3.iloc[i, TTC_3] = dc3.iloc[i, n10T_3]*dc3_params.iloc[1, SC10T_3] + dc3.iloc[i, n20T_3]*dc3_params.iloc[1, SC20T_3]
    
    # Product Cost
    dc3.iloc[i, PC_3] = dc3.iloc[i, PUC_3]*dc3.iloc[i, PO_3]
    
    # Total Supply Cost
    dc3.iloc[i, TSC_3] = dc3.iloc[i, TTC_3] + dc3.iloc[i, PC_3]
    
    # Revenue
    dc3.iloc[i, REV_3] = dc3.iloc[i, PSP_3]*dc3.iloc[i, PO_3]
    
    # Profit
    dc3.iloc[i, PF_3] = dc3.iloc[i, REV_3] - dc3.iloc[i, TSC_3]
    
    # Spot Demand
    dc3.iloc[i, SD_3] = dc3.iloc[i + int(dc3_params.iloc[0, LT_3]), SFD_3] + dc3.iloc[i + int(dc3_params.iloc[0, LT_3]), SO_3]

dc3['Updated Spot Forecast Demand'] = dc3['Spot Forecast Demand(MT)']

#%% Supplier

supp_params = pd.read_excel('demand_data.xlsx',sheet_name='Sup', skiprows = 2, nrows= 6, usecols = 'B:C')
supp_params.index = supp_params['Category']
supp_params.drop('Category', axis=1, inplace=True)
supp_params = supp_params.transpose().fillna(0)

FD = dc1['Planned Orders (MT)'] + dc2['Planned Orders (MT)'] + dc3['Planned Orders (MT)']
supp = FD.to_frame().rename(columns={'Planned Orders (MT)': 'Supplier Demand'})
supp['Proj End Inv'] = 0
supp['Net Requirements'] = 0
supp['Master Production Schedule'] = 0
supp['Planned Orders (MT)'] = 0
supp['Spot to reduce'] = 0
supp['Amount to Move'] = 0
supp['Updated MPS'] = 0

# Initial Net Requirements

if supp_params.loc['Value','Initial Ending Inventory (MT)'] - supp.loc[first_week, 'Supplier Demand'] <= supp_params.loc['Value', 'Safety Stock (MT)']:
    supp.loc[first_week, 'Net Requirements'] = supp.loc[first_week, 'Supplier Demand'] - supp_params.loc['Value','Initial Ending Inventory (MT)'] + supp_params.loc['Value', 'Safety Stock (MT)']

else:
    supp.loc[first_week, 'Net Requirements'] = 0

# Initial Master Production Schedule
supp.loc[first_week, 'Master Production Schedule'] = math.ceil(supp.loc[first_week, 'Net Requirements']/supp_params.loc['Value','Lot Size (MT)'])*supp_params.loc['Value','Lot Size (MT)']

# Initial Project Ending Inventory
supp.loc[first_week,'Proj End Inv'] = supp_params.loc['Value','Initial Ending Inventory (MT)'] +\
                                    supp.loc[first_week,'Master Production Schedule'] -\
                                    supp.loc[first_week,'Supplier Demand']

PEI_supp = supp.columns.get_loc('Proj End Inv')
MPS_supp = supp.columns.get_loc('Master Production Schedule')
NR_supp = supp.columns.get_loc('Net Requirements')
SD_supp = supp.columns.get_loc('Supplier Demand')
PO_supp = supp.columns.get_loc('Planned Orders (MT)')
STR_supp = supp.columns.get_loc('Spot to reduce')
ATM_supp = supp.columns.get_loc('Amount to Move')
UMPS_supp = supp.columns.get_loc('Updated MPS')

SS_supp = supp_params.columns.get_loc('Safety Stock (MT)')
LT_supp = supp_params.columns.get_loc('Lead Time (weeks)')
LS_supp = supp_params.columns.get_loc('Lot Size (MT)')
MDP_supp = supp_params.columns.get_loc('Max Daily Production')
MT_supp = supp_params.columns.get_loc('Method')

if supp_params.iloc[0, MT_supp] == 'Cut':
    print('Cut method selected.')
else:
    print('Move method selected.')

#%% Calculating profit loss for each Demand Centre
amt_to_reduce = 0

# Spot Demand to reduce
for i in range(0, len(supp)):
    
    if i > 0:

        # Net Requirements
        
        if supp.iloc[i-1, PEI_supp] - supp.iloc[i, SD_supp] <= supp_params.iloc[0, SS_supp]:
            supp.iloc[i, NR_supp] = supp.iloc[i, SD_supp] - supp.iloc[i-1, PEI_supp] + supp_params.iloc[0, SS_supp]
            
        else:
            supp.iloc[i, NR_supp] = 0
        
        # Master Production Schedule
        
        if i >= supp_params.iloc[0, LT_supp]:
            supp.iloc[i, MPS_supp] = math.ceil(supp.iloc[i, NR_supp]/supp_params.iloc[0, LS_supp])*supp_params.iloc[0, LS_supp]
            supp.iloc[i, UMPS_supp] = supp.iloc[i, MPS_supp]
        # Projected Ending Inventory
        
        supp.iloc[i, PEI_supp] = supp.iloc[i-1, PEI_supp] + supp.iloc[i, MPS_supp] - supp.iloc[i, SD_supp]

    if i < len(supp)-int(supp_params.iloc[0, LT_supp]):
        
        # Planned Orders
        supp.iloc[i - int(supp_params.iloc[0, LT_supp]), PO_supp] = supp.iloc[i, MPS_supp]
        
        # Supplier Amount to Reduce
        if supp.iloc[i, NR_supp] - supp_params.iloc[0, MDP_supp] >=0:
            
            # Amount to Reduce
            supp.iloc[i, STR_supp] = supp.iloc[i, NR_supp] - supp_params.iloc[0, MDP_supp] - amt_to_reduce
            
            # Amount to Move
            supp.iloc[i, ATM_supp] = supp.iloc[i, MPS_supp] - supp_params.iloc[0, MDP_supp]
        else:
            supp.iloc[i, STR_supp] = 0
            supp.iloc[i, ATM_supp] = 0
    
    if supp_params.iloc[0, MT_supp] == 'Cut':
            
        # Spot Demand to Reduce - DC1, DC2, DC3
        
        if i < len(dc1) - int(dc1_params.iloc[0, LT_1]):
            dc1.iloc[i, SDTR_1] = min(max(supp.iloc[i, STR_supp] - (dc1.iloc[i + int(dc1_params.iloc[0, LT_1]), PR_1] - dc1.iloc[i + int(dc1_params.iloc[0, LT_1]), NR_1]),0) , dc1.iloc[i, SD_1])
                  
        if i < len(dc2) - int(dc2_params.iloc[0, LT_2]):
            dc2.iloc[i, SDTR_2] = min(max(supp.iloc[i, STR_supp] - (dc2.iloc[i + int(dc2_params.iloc[0, LT_2]), PR_2] - dc2.iloc[i + int(dc2_params.iloc[0, LT_2]), NR_2]),0) , dc2.iloc[i, SD_2])
        
        if i < len(dc3) - int(dc3_params.iloc[0, LT_3]):
            dc3.iloc[i, SDTR_3] = min(max(supp.iloc[i, STR_supp] - (dc3.iloc[i + int(dc3_params.iloc[0, LT_3]), PR_3] - dc3.iloc[i + int(dc3_params.iloc[0, LT_3]), NR_3]),0) , dc3.iloc[i, SD_3])
        
        # Spot truck count - DC1
        dc1.iloc[i, Sn10T_1] = ((dc1.iloc[i, SDTR_1] + dc1_params.iloc[0, SC10T_1] - 1)%dc1_params.iloc[0, SC20T_1])//dc1_params.iloc[0, SC10T_1]
        dc1.iloc[i, Sn20T_1] = (dc1.iloc[i, SDTR_1] + dc1_params.iloc[0, SC10T_1] - 1)//dc1_params.iloc[0, SC20T_1]
        
        # Spot truck count - DC2
        dc2.iloc[i, Sn10T_2] = ((dc2.iloc[i, SDTR_2] + dc2_params.iloc[0, SC10T_2] - 1)%dc2_params.iloc[0, SC20T_2])//dc2_params.iloc[0, SC10T_2]
        dc2.iloc[i, Sn20T_2] = (dc2.iloc[i, SDTR_2] + dc2_params.iloc[0, SC10T_2] - 1)//dc2_params.iloc[0, SC20T_2]
        
        # Spot truck count - DC3
        dc3.iloc[i, Sn10T_3] = ((dc3.iloc[i, SDTR_3] + dc3_params.iloc[0, SC10T_3] - 1)%dc3_params.iloc[0, SC20T_3])//dc3_params.iloc[0, SC10T_3]
        dc3.iloc[i, Sn20T_3] = (dc3.iloc[i, SDTR_3] + dc3_params.iloc[0, SC10T_3] - 1)//dc3_params.iloc[0, SC20T_3]
        
        # Spot Transportation cost - DC1, DC2, DC3
        dc1.iloc[i, STC_1] = dc1.iloc[i, Sn10T_1]*dc1_params.iloc[1, SC10T_1] + dc1.iloc[i, Sn20T_1]*dc1_params.iloc[1, SC20T_1]
        dc2.iloc[i, STC_2] = dc2.iloc[i, Sn10T_2]*dc2_params.iloc[1, SC10T_2] + dc2.iloc[i, Sn20T_2]*dc2_params.iloc[1, SC20T_2]
        dc3.iloc[i, STC_3] = dc3.iloc[i, Sn10T_3]*dc3_params.iloc[1, SC10T_3] + dc3.iloc[i, Sn20T_3]*dc3_params.iloc[1, SC20T_3]
        
        # Spot Product Cost
        dc1.iloc[i, SPC_1] = dc1.iloc[i, PUC_1]*dc1.iloc[i, SDTR_1]
        dc2.iloc[i, SPC_2] = dc2.iloc[i, PUC_2]*dc2.iloc[i, SDTR_2]
        dc3.iloc[i, SPC_3] = dc3.iloc[i, PUC_3]*dc3.iloc[i, SDTR_3]
        
        # Spot Supply Cost
        dc1.iloc[i, SSC_1] = dc1.iloc[i, STC_1] + dc1.iloc[i, SPC_1]
        dc2.iloc[i, SSC_2] = dc2.iloc[i, STC_2] + dc2.iloc[i, SPC_2]
        dc3.iloc[i, SSC_3] = dc3.iloc[i, STC_3] + dc3.iloc[i, SPC_3]
        
        # Spot Revenue
        dc1.iloc[i, SRev_1] = dc1.iloc[i, PSP_1]*dc1.iloc[i, SDTR_1]
        dc2.iloc[i, SRev_2] = dc2.iloc[i, PSP_2]*dc2.iloc[i, SDTR_2]
        dc3.iloc[i, SRev_3] = dc3.iloc[i, PSP_3]*dc3.iloc[i, SDTR_3]
        
        # Spot Profit
        dc1.iloc[i, SP_1] = dc1.iloc[i, SRev_1] - dc1.iloc[i, SSC_1]
        dc2.iloc[i, SP_2] = dc2.iloc[i, SRev_2] - dc2.iloc[i, SSC_2]
        dc3.iloc[i, SP_3] = dc3.iloc[i, SRev_3] - dc3.iloc[i, SSC_3]
    
    #%% Optimisation
        
        # Spot Profit
        spot_pf1 = dc1.iloc[i, SP_1]
        spot_pf2 = dc2.iloc[i, SP_2]
        spot_pf3 = dc3.iloc[i, SP_3]
        
        buffer = 8  # This is just assumption for the algo to work. Needs a more concrete value.
        
        # Setting spot profit to high value to prevent from being selected during minimisation.
        if int(dc1.iloc[i, SD_1]) < supp.iloc[i, STR_supp] - buffer:
            spot_pf1 = 1e5
            
        if int(dc2.iloc[i, SD_2]) < supp.iloc[i, STR_supp] - buffer:
            spot_pf2 = 1e5
            
        if int(dc3.iloc[i, SD_3]) < supp.iloc[i, STR_supp] - buffer:
            spot_pf3 = 1e5
        
        min_list = [spot_pf1,spot_pf2,spot_pf3]
        min_value = int(min(min_list))
        
        # Getting minimum profit Demand centre (DC1, DC2, or DC3)
        index_min = min(range(len(min_list)),key=min_list.__getitem__)
        
        if min_value > 0:
            
            if index_min==0:    # Demand Centre 1
                print(f"For best profit, it is recommended to reduce Spot Order for Demand Centre 1 in {dc1.index[i + int(dc1_params.iloc[0, LT_1])]} by {int(dc1.iloc[i, SDTR_1])} MT.")
                amt_to_reduce = amt_to_reduce + int(dc1.iloc[i, SDTR_1])
                dc1.iloc[i + int(dc1_params.iloc[0, LT_1]), USFD_1] = dc1.iloc[i + int(dc1_params.iloc[0, LT_1]), USFD_1] - int(dc1.iloc[i, SDTR_1])
                
            elif index_min==1:  # Demand Centre 2
                print(f"For best profit, it is recommended to reduce Spot Order for Demand Centre 2 in {dc2.index[i + int(dc2_params.iloc[0, LT_2])]} by {int(dc2.iloc[i, SDTR_2])} MT.")
                amt_to_reduce = amt_to_reduce + int(dc2.iloc[i, SDTR_2])
                dc2.iloc[i + int(dc2_params.iloc[0, LT_2]), USFD_2] = dc2.iloc[i + int(dc2_params.iloc[0, LT_2]), USFD_2] - int(dc2.iloc[i, SDTR_2])
                
            else:               # Demand Centre 3
                print(f"For best profit, it is recommended to reduce Spot Order for Demand Centre 3 in {dc3.index[i + int(dc3_params.iloc[0, LT_3])]} by {int(dc3.iloc[i, SDTR_3])} MT.")
                amt_to_reduce = amt_to_reduce + int(dc3.iloc[i, SDTR_3])
                dc3.iloc[i + int(dc3_params.iloc[0, LT_3]), USFD_3] = dc3.iloc[i + int(dc3_params.iloc[0, LT_3]), USFD_3] - int(dc3.iloc[i, SDTR_3])

    else:   # Move
        
        supp.iloc[i, UMPS_supp] = supp.iloc[i, MPS_supp] - supp.iloc[i, ATM_supp]
        ind_move = 1
        
        while supp.iloc[i, ATM_supp] != 0:            
                                    
            if supp.iloc[i-ind_move, UMPS_supp] < supp_params.iloc[0, MDP_supp]:
                supp.iloc[i-ind_move, UMPS_supp] = supp.iloc[i-ind_move, UMPS_supp] + supp_params.iloc[0, LS_supp]
                supp.iloc[i, ATM_supp] = supp.iloc[i, ATM_supp] - supp_params.iloc[0, LS_supp]
                
            else:
                ind_move +=1
        
        # Planned Orders
        supp.iloc[i - int(supp_params.iloc[0, LT_supp]), PO_supp] = supp.iloc[i, UMPS_supp]

if supp_params.iloc[0, MT_supp] == 'Cut':
    pass

else:
    for i in range(0,len(supp) - int(supp_params.iloc[0, LT_supp])):
        supp.iloc[i, PO_supp] = supp.iloc[i+int(supp_params.iloc[0, LT_supp]), UMPS_supp]
    
    print ('MPS Orders Moved successfully.')
    print (f'Before: \n{supp.iloc[:, MPS_supp]}')    
    print (f'After: \n{supp.iloc[:, UMPS_supp]}')