# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 08:20:05 2020

@author: James Ang
"""

import json
import math
import copy
import pandas as pd

class Hospital:
    
    def __init__(self, data):
        
        self.data = data
        # self.hosp_num = hosp_num
        self.name = self.data.get('name')        
        self.demand_table = pd.DataFrame(self.data.get('weekly_consumption'))

        # self.table_temp = copy.deepcopy(self.table)
        self.demand_table.index = self.demand_table.week
        
        # self.demand_table.drop(['demand'], axis=1, inplace=True)
        # self.total_demand = self.demand_table.iloc[:,1]
        self.supplier_leadtime = self.data.get('supplier_leadtime')
        self.total_demand = self.demand_table.loc[:,'quantity']
        self.proj_end_inv = pd.Series(data=[0]*len(self.demand_table), index = self.demand_table.index,name='proj_end_inv')
        self.planned_receipts_table = pd.DataFrame(self.data.get('weekly_allocation_plan'))
        self.planned_receipts_table.index = self.planned_receipts_table.week
        self.planned_receipts = self.planned_receipts_table.loc[:,'quantity']
        self.demandto_supplier = pd.Series(data=[0]*len(self.demand_table), index = self.demand_table.index,name='demand_to_supplier')
        
        
        
        # Convert days to weeks
        if self.data.get('supply_lead_time')<7:
            self.supplier_leadtime  = 0
        elif self.data.get('supply_lead_time')<14:
            self.supplier_leadtime  = 1
        elif self.data.get('supply_lead_time')<21:
            self.supplier_leadtime  = 2
        else:
            pass
        
        for i in range(0,len(self.demand_table)-self.supplier_leadtime):
            # print(i)
            self.demandto_supplier[i] = self.planned_receipts[i+self.supplier_leadtime]
        # self.supply_lotsize = self.data.get('supply_lot_size')
        self.safety_stock = self.data.get('safety_stock')
        self.max_inv = self.data.get('maximum_inventory')
        self.iei = self.data.get('initial_ending_inventory')
    #     self.planned_orders = pd.Series(data=[0]*len(self.demand_table), index = self.demand_table.index, name ='planned_orders')        
    #     self.net_requirements_safety = pd.Series(data=[0]*len(self.demand_table), index = self.demand_table.index,name ='net_requirements_safety')
        
        # DC INITIALISATIONS
    #     # Net Requirements            
    #     if self.iei + self.demand_table['confirmed_order'][0] - self.total_demand[0] <= self.safety_stock:
    #         self.net_requirements_safety[0] = self.total_demand[0] - self.iei - self.demand_table['confirmed_order'][0] + self.safety_stock
    #     else:
    #         self.net_requirements_safety[0] = 0
        
        # # Planned Receipts
        # self.planned_receipts[0] = math.ceil(self.net_requirements_safety[0]/self.supply_lotsize)*self.supply_lotsize
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.planned_receipts[0] - self.total_demand[0]
        
        for i in range(1, len(self.demand_table)):
            # print(i)
    #         # Net Requirements
    #         if self.proj_end_inv[i-1] + self.demand_table['confirmed_order'][i] - self.total_demand[i] <= self.safety_stock:
    #             self.net_requirements_safety[i] = self.total_demand[i] - self.proj_end_inv[i-1] - self.demand_table['confirmed_order'][i] + self.safety_stock
    #         else:
    #             self.net_requirements_safety[i] = 0
            
            # # Planned Receipts
            # if i >= self.supplier_leadtime:
            #     self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.total_demand[i]

        self.table_final = pd.concat([
            self.demand_table,
            # self.truck_count_initial, 
            self.proj_end_inv,
            # self.replenishment_initial,
            # self.truck_count_final, 
            # self.proj_end_inv_final, 
            # self.replenishment_final
            ],axis=1)
        self.table_final.drop(['quantity'], axis=1, inplace=True)

        self.table_final = json.loads(self.table_final.to_json(orient='records'))
        

    
class Warehouse:
    
    def __init__(self, data):
        
        self.data = data
        # self.hosp_num = hosp_num
        self.name = self.data.get('name')        
        self.demand_table = pd.DataFrame(self.data.get('weekly_consumption'))
        self.supplier_leadtime = self.data.get('supplier_leadtime')
        # self.table_temp = copy.deepcopy(self.table)
        self.demand_table.index = self.demand_table.week
        
        # self.demand_table.drop(['demand'], axis=1, inplace=True)
        # self.total_demand = self.demand_table.iloc[:,1]
        self.total_demand = self.demand_table.loc[:,'quantity']
        self.proj_end_inv = pd.Series(data=[0]*len(self.demand_table), index = self.demand_table.index,name='proj_end_inv')
        self.planned_receipts_table = pd.DataFrame(self.data.get('weekly_allocation_plan'))
        self.planned_receipts_table.index = self.planned_receipts_table.week
        self.planned_receipts = self.planned_receipts_table.loc[:,'quantity']
        self.demandto_supplier = pd.Series(data=[0]*len(self.demand_table), index = self.demand_table.index,name='demand_to_supplier')
        
        
        # Convert days to weeks
        if self.data.get('supply_lead_time')<7:
            self.supplier_leadtime  = 0
        elif self.data.get('supply_lead_time')<14:
            self.supplier_leadtime  = 1
        elif self.data.get('supply_lead_time')<21:
            self.supplier_leadtime  = 2
        else:
            pass
        
        for i in range(0,len(self.demand_table)-self.supplier_leadtime):
            # print(i)
            self.demandto_supplier[i] = self.planned_receipts[i+self.supplier_leadtime]
        # self.supply_lotsize = self.data.get('supply_lot_size')
        self.safety_stock = self.data.get('safety_stock')
        self.max_inv = self.data.get('maximum_inventory')
        self.iei = self.data.get('initial_ending_inventory')
    #     self.planned_orders = pd.Series(data=[0]*len(self.demand_table), index = self.demand_table.index, name ='planned_orders')        
    #     self.net_requirements_safety = pd.Series(data=[0]*len(self.demand_table), index = self.demand_table.index,name ='net_requirements_safety')
        
        # DC INITIALISATIONS
    #     # Net Requirements            
    #     if self.iei + self.demand_table['confirmed_order'][0] - self.total_demand[0] <= self.safety_stock:
    #         self.net_requirements_safety[0] = self.total_demand[0] - self.iei - self.demand_table['confirmed_order'][0] + self.safety_stock
    #     else:
    #         self.net_requirements_safety[0] = 0
        
        # # Planned Receipts
        # self.planned_receipts[0] = math.ceil(self.net_requirements_safety[0]/self.supply_lotsize)*self.supply_lotsize
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.planned_receipts[0] - self.total_demand[0]
        
        for i in range(1, len(self.demand_table)):
            # print(i)
    #         # Net Requirements
    #         if self.proj_end_inv[i-1] + self.demand_table['confirmed_order'][i] - self.total_demand[i] <= self.safety_stock:
    #             self.net_requirements_safety[i] = self.total_demand[i] - self.proj_end_inv[i-1] - self.demand_table['confirmed_order'][i] + self.safety_stock
    #         else:
    #             self.net_requirements_safety[i] = 0
            
            # # Planned Receipts
            # if i >= self.supplier_leadtime:
            #     self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.total_demand[i]

        self.table_final = pd.concat([
            self.demand_table,
            # self.truck_count_initial, 
            self.proj_end_inv,
            # self.replenishment_initial,
            # self.truck_count_final, 
            # self.proj_end_inv_final, 
            # self.replenishment_final
            ],axis=1)
        self.table_final.drop(['quantity'], axis=1, inplace=True)

        self.table_final = json.loads(self.table_final.to_json(orient='records'))
        
 

class Supplier:
    
    def __init__(self, data, hospitals, warehouses):
        
        self.data = data
        self.name = self.data.get('name')
        self.supply_to = self.data.get('supply_to')
        self.hospitals = hospitals
        self.warehouses = warehouses
        
        self.relevant_entity = []

        for hospital in self.hospitals:
            
            if hospital.name in self.supply_to:
                self.relevant_entity.append(hospital)
        
        for warehouse in self.warehouses:
            
            if warehouse.name in self.supply_to:
                self.relevant_entity.append(warehouse)
                
        self.consumption = pd. concat([data.demandto_supplier for data in self.relevant_entity],axis=1)
        self.total_consumption = pd.DataFrame(self.consumption).sum(axis=1)
        self.total_consumption.name = 'total demand quantity'

    #     self.table = pd.DataFrame(self.data.get('supply_quarantine'))
    #     self.table.index = self.table.week
    #     # self.table.drop('week', axis=1, inplace=True)
    #     self.total_demand = supplier_demand
        self.proj_end_inv = pd.Series(data=[0]*len(self.total_consumption), index = self.total_consumption.index, name = 'proj_end_inv')
        self.planned_receipts_table = pd.DataFrame(self.data.get('supply_after_quarantine'))
        self.planned_receipts_table.index = self.planned_receipts_table.week
        self.planned_receipts = self.planned_receipts_table.loc[:,'quantity']
    #     self.planned_receipts = pd.Series(data=[0]*len(self.table), index = self.table.index, name = 'planned_receipts')
    #     # self.supply_quarantine = self.table.iloc[:,1]
    #     self.supply_quarantine = self.table.loc[:,'confirmed_order']
        
    # # Convert days to weeks
    #     if self.data.get('quarantine_lead_time')<7:
    #         self.quarantine_lead_time  = 0
    #     elif self.data.get('quarantine_lead_time')<14:
    #         self.quarantine_lead_time  = 1
    #     elif self.data.get('quarantine_lead_time')<21:
    #         self.quarantine_lead_time  = 2
    #     else:
    #         pass
        self.safety_stock = self.data.get('safety_stock')
        self.max_inv = self.data.get('maximum_inventory')
        self.iei = self.data.get('initial_ending_inventory')
    # #     self.planned_orders = pd.Series(data=[0]*len(self.table), index = self.table.index)        
    # #     self.net_requirements_safety = pd.Series(data=[0]*len(self.table), index = self.table.index)
        
    #     # DC INITIALISATIONS
    #     # Net Requirements            
    # #     if self.iei + self.table['confirmed_order'][0] - self.total_demand[0] <= self.safety_stock:
    # #         self.net_requirements_safety[0] = self.total_demand[0] - self.iei - self.table['confirmed_order'][0] + self.safety_stock
    # #     else:
    # #         self.net_requirements_safety[0] = 0
        
        
    #     # Planned Receipts
    #     for i in range(0, len(self.table)-int(self.quarantine_lead_time)):
            
    #         self.planned_receipts[i+int(self.quarantine_lead_time)] = self.supply_quarantine[i]
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.planned_receipts[0] - self.total_consumption[0]
        
        for i in range(1, len(self.total_consumption)):
    
    # #         # Net Requirements
    # #         if self.proj_end_inv[i-1] + self.table['confirmed_order'][i] - self.total_demand[i] <= self.safety_stock:
    # #             self.net_requirements_safety[i] = self.total_demand[i] - self.proj_end_inv[i-1] - self.table['confirmed_order'][i] + self.safety_stock
    # #         else:
    # #             self.net_requirements_safety[i] = 0
            
    # #         # Planned Receipts
    # #         if i >= self.supplier_leadtime:
    # #             self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.total_consumption[i]

        
        self.table_final = pd.concat([
            self.planned_receipts_table,
            self.total_consumption, 
            self.proj_end_inv,
            # self.replenishment_initial,
            # self.truck_count_final, 
            # self.proj_end_inv_final, 
            # self.replenishment_final
            ],axis=1)
        self.table_final.drop(['quantity'], axis=1, inplace=True)

        self.table_final = json.loads(self.table_final.to_json(orient='records'))
        
    