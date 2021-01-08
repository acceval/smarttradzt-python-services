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
    
    def __init__(self, data, hosp_num = 0):
        
        self.data = data
        self.hosp_num = hosp_num
        self.name = self.data[self.hosp_num].get('name')        
        self.table = pd.DataFrame(self.data[self.hosp_num].get('weekly_allocation_plan'))
        # self.table_temp = copy.deepcopy(self.table)
        self.table.index = self.table.week
        # self.table.drop(['demand'], axis=1, inplace=True)
        # self.total_demand = self.table.iloc[:,1]
        self.total_demand = self.table.loc[:,'demand']
        self.proj_end_inv = pd.Series(data=[0]*len(self.table), index = self.table.index,name='proj_end_inv')
        self.planned_receipts = pd.Series(data=[0]*len(self.table), index = self.table.index, name ='planned_receipts')
        
        # Convert days to weeks
        if self.data[self.hosp_num].get('supply_lead_time')<7:
            self.supplier_leadtime  = 0
        elif self.data[self.hosp_num].get('supply_lead_time')<14:
            self.supplier_leadtime  = 1
        elif self.data[self.hosp_num].get('supply_lead_time')<21:
            self.supplier_leadtime  = 2
        else:
            pass
            
        self.supply_lotsize = self.data[self.hosp_num].get('supply_lot_size')
        self.safety_stock = self.data[self.hosp_num].get('safety_stock')
        self.max_inv = self.data[self.hosp_num].get('maximum_inventory')
        self.iei = self.data[self.hosp_num].get('initial_ending_inventory')
        self.planned_orders = pd.Series(data=[0]*len(self.table), index = self.table.index, name ='planned_orders')        
        self.net_requirements_safety = pd.Series(data=[0]*len(self.table), index = self.table.index,name ='net_requirements_safety')
        
        # DC INITIALISATIONS
        # Net Requirements            
        if self.iei + self.table['confirmed_order'][0] - self.total_demand[0] <= self.safety_stock:
            self.net_requirements_safety[0] = self.total_demand[0] - self.iei - self.table['confirmed_order'][0] + self.safety_stock
        else:
            self.net_requirements_safety[0] = 0
        
        # Planned Receipts
        self.planned_receipts[0] = math.ceil(self.net_requirements_safety[0]/self.supply_lotsize)*self.supply_lotsize
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.table['confirmed_order'][0] + self.planned_receipts[0] - self.total_demand[0]
        
        for i in range(1, len(self.table)):
    
            # Net Requirements
            if self.proj_end_inv[i-1] + self.table['confirmed_order'][i] - self.total_demand[i] <= self.safety_stock:
                self.net_requirements_safety[i] = self.total_demand[i] - self.proj_end_inv[i-1] - self.table['confirmed_order'][i] + self.safety_stock
            else:
                self.net_requirements_safety[i] = 0
            
            # Planned Receipts
            if i >= self.supplier_leadtime:
                self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.table['confirmed_order'][i] + self.planned_receipts[i] - self.total_demand[i]

        
    def calc(self):
        
        for i in range(0, len(self.table)-int(self.supplier_leadtime)):
            
            # Planned Orders
            self.planned_orders[i] = self.planned_receipts[i + int(self.supplier_leadtime)] 
        
        self.table_final = pd.concat([self.table, self.proj_end_inv,self.net_requirements_safety, self.planned_receipts, self.planned_orders],axis=1)
        self.table_final.drop(['demand','confirmed_order'], axis=1, inplace=True)
        self.table_final = json.loads(self.table_final.to_json(orient='records'))
        self.table = json.loads(self.table.to_json())
        
        self.total_demand = json.loads(self.total_demand.to_json())
        self.net_requirements_safety = json.loads(self.net_requirements_safety.to_json())
        self.planned_orders = json.loads(self.planned_orders.to_json())
        self.proj_end_inv = json.loads(self.proj_end_inv.to_json())
        self.planned_receipts = json.loads(self.planned_receipts.to_json())
        
        return self.planned_orders
    

class Demand_Centre:
    
    def __init__(self, data, warehouse_demand):
        
        self.data = data[0]
    #     # self.hosp_num = hosp_num
        self.name = self.data.get('name')        
        self.table = pd.DataFrame(self.data.get('weekly_allocation_plan'))
        self.table.index = self.table.week
        # self.table.drop('week', axis=1, inplace=True)
        self.total_demand = warehouse_demand
        self.proj_end_inv = pd.Series(data=[0]*len(self.table), index = self.table.index, name ='proj_end_inv')
        self.planned_receipts = pd.Series(data=[0]*len(self.table), index = self.table.index, name ='planned_receipts')
        self.supplier_leadtime  = self.data.get('supply_lead_time')
        self.supply_lotsize = self.data.get('supply_lot_size')
        self.safety_stock = self.data.get('safety_stock')
        self.max_inv = self.data.get('maximum_inventory')
        self.iei = self.data.get('initial_ending_inventory')
        self.planned_orders = pd.Series(data=[0]*len(self.table), index = self.table.index, name ='planned_orders')        
        self.net_requirements_safety = pd.Series(data=[0]*len(self.table), index = self.table.index, name ='net_requirements_safety')
        
        # DC INITIALISATIONS
        # Net Requirements            
        if self.iei + self.table['confirmed_order'][0] - self.total_demand[0] <= self.safety_stock:
            self.net_requirements_safety[0] = self.total_demand[0] - self.iei - self.table['confirmed_order'][0] + self.safety_stock
        else:
            self.net_requirements_safety[0] = 0
        
          # Planned Receipts
        self.planned_receipts[0] = math.ceil(self.net_requirements_safety[0]/self.supply_lotsize)*self.supply_lotsize
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.table['confirmed_order'][0] + self.planned_receipts[0] - self.total_demand[0]
        
        for i in range(1, len(self.table)):
    
            # Net Requirements
            if self.proj_end_inv[i-1] + self.table['confirmed_order'][i] - self.total_demand[i] <= self.safety_stock:
                self.net_requirements_safety[i] = self.total_demand[i] - self.proj_end_inv[i-1] - self.table['confirmed_order'][i] + self.safety_stock
            else:
                self.net_requirements_safety[i] = 0
            
            # Planned Receipts
            if i >= self.supplier_leadtime:
                self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.table['confirmed_order'][i] + self.planned_receipts[i] - self.total_demand[i]

        
    def calc(self):
        
        for i in range(0, len(self.table)-int(self.supplier_leadtime)):
            
            # Planned Orders
            self.planned_orders[i] = self.planned_receipts[i + int(self.supplier_leadtime)] 
        
        self.table_final = pd.concat([self.table, self.proj_end_inv,self.net_requirements_safety, self.planned_receipts, self.planned_orders],axis=1)
        self.table_final.drop(['confirmed_order'], axis=1, inplace=True)
        self.table_final = json.loads(self.table_final.to_json(orient='records'))
        self.table = json.loads(self.table.to_json())
        self.total_demand = json.loads(self.total_demand.to_json())
        self.net_requirements_safety = json.loads(self.net_requirements_safety.to_json())
        self.planned_orders = json.loads(self.planned_orders.to_json())
        self.proj_end_inv = json.loads(self.proj_end_inv.to_json())
        self.planned_receipts = json.loads(self.planned_receipts.to_json())
        
        return self.planned_orders
    


class Supplier:
    
    def __init__(self, data, supplier_demand):
        
        self.data = data[0]
    #     # self.hosp_num = hosp_num
        self.name = self.data.get('name')        
        self.table = pd.DataFrame(self.data.get('supply_quarantine'))
        self.table.index = self.table.week
        # self.table.drop('week', axis=1, inplace=True)
        self.total_demand = supplier_demand
        self.proj_end_inv = pd.Series(data=[0]*len(self.table), index = self.table.index, name = 'proj_end_inv')
        self.planned_receipts = pd.Series(data=[0]*len(self.table), index = self.table.index, name = 'planned_receipts')
        # self.supply_quarantine = self.table.iloc[:,1]
        self.supply_quarantine = self.table.loc[:,'confirmed_order']
        
    # Convert days to weeks
        if self.data.get('quarantine_lead_time')<7:
            self.quarantine_lead_time  = 0
        elif self.data.get('quarantine_lead_time')<14:
            self.quarantine_lead_time  = 1
        elif self.data.get('quarantine_lead_time')<21:
            self.quarantine_lead_time  = 2
        else:
            pass
        
        
        

        self.safety_stock = self.data.get('safety_stock')
        self.max_inv = self.data.get('maximum_inventory')
        self.iei = self.data.get('initial_ending_inventory')
    #     self.planned_orders = pd.Series(data=[0]*len(self.table), index = self.table.index)        
    #     self.net_requirements_safety = pd.Series(data=[0]*len(self.table), index = self.table.index)
        
        # DC INITIALISATIONS
        # Net Requirements            
    #     if self.iei + self.table['confirmed_order'][0] - self.total_demand[0] <= self.safety_stock:
    #         self.net_requirements_safety[0] = self.total_demand[0] - self.iei - self.table['confirmed_order'][0] + self.safety_stock
    #     else:
    #         self.net_requirements_safety[0] = 0
        
           
        # Planned Receipts
        for i in range(0, len(self.table)-int(self.quarantine_lead_time)):
            
            self.planned_receipts[i+int(self.quarantine_lead_time)] = self.supply_quarantine[i]
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.planned_receipts[0] - self.total_demand[0]
        
        for i in range(1, len(self.table)):
    
    #         # Net Requirements
    #         if self.proj_end_inv[i-1] + self.table['confirmed_order'][i] - self.total_demand[i] <= self.safety_stock:
    #             self.net_requirements_safety[i] = self.total_demand[i] - self.proj_end_inv[i-1] - self.table['confirmed_order'][i] + self.safety_stock
    #         else:
    #             self.net_requirements_safety[i] = 0
            
    #         # Planned Receipts
    #         if i >= self.supplier_leadtime:
    #             self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.total_demand[i]

        
    def calc(self):
        
    #     for i in range(0, len(self.table)-int(self.supplier_leadtime)):
            
    #         # Planned Orders
    #         self.planned_orders[i] = self.planned_receipts[i + int(self.supplier_leadtime)] 
        self.table_final = pd.concat([self.table, self.proj_end_inv, self.planned_receipts],axis=1)
        self.table_final.drop(['confirmed_order'], axis=1, inplace=True)
        self.table_final = json.loads(self.table_final.to_json(orient='records'))
        self.table = json.loads(self.table.to_json())
    #     self.total_demand = json.loads(self.total_demand.to_json())
    #     self.net_requirements_safety = json.loads(self.net_requirements_safety.to_json())
    #     self.planned_orders = json.loads(self.planned_orders.to_json())
        self.proj_end_inv = json.loads(self.proj_end_inv.to_json())
        self.supply_quarantine = json.loads(self.supply_quarantine.to_json())
        self.planned_receipts = json.loads(self.planned_receipts.to_json())
        
        return self.proj_end_inv
    


class Dry_Ice_Supplier:
    
    def __init__(self, data, dryice_demand):
        
        self.data = data[0]
    #     # self.hosp_num = hosp_num
        self.name = self.data.get('name')        
        self.table = pd.DataFrame(self.data.get('weekly_allocation_plan'))
        self.table.index = self.table.week
        # self.table.drop('week', axis=1, inplace=True)
        self.conversion = self.data.get("dry_ice_weight_perbox")
        self.total_demand = dryice_demand*self.conversion
        self.proj_end_inv = pd.Series(data=[0]*len(self.table), index = self.table.index, name = 'proj_end_inv')
        self.planned_receipts = pd.Series(data=[0]*len(self.table), index = self.table.index, name = 'planned_receipts')
        if self.data.get('sourcing_lead_time')<7:
            self.sourcing_lead_time  = 0
        elif self.data.get('sourcing_lead_time')<14:
            self.sourcing_lead_time  = 1
        elif self.data.get('sourcing_lead_time')<21:
            self.sourcing_lead_time  = 2
        else:
            pass
       
        self.supply_lotsize = self.data.get('sourcing_lot_size')
        self.safety_stock = self.data.get('safety_stock')
        self.max_inv = self.data.get('maximum_inventory')
        self.iei = self.data.get('initial_ending_inventory')
        self.planned_orders = pd.Series(data=[0]*len(self.table), index = self.table.index,name = 'planned_orders')        
        self.net_requirements_safety = pd.Series(data=[0]*len(self.table), index = self.table.index,name = 'net_requirements_safety')
        
        # DC INITIALISATIONS
        # Net Requirements            
        if self.iei + self.table['confirmed_order'][0] - self.total_demand[0] <= self.safety_stock:
            self.net_requirements_safety[0] = self.total_demand[0] - self.iei - self.table['confirmed_order'][0] + self.safety_stock
        else:
            self.net_requirements_safety[0] = 0
        
          # Planned Receipts
        self.planned_receipts[0] = math.ceil(self.net_requirements_safety[0]/self.supply_lotsize)*self.supply_lotsize
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.table['confirmed_order'][0] + self.planned_receipts[0] - self.total_demand[0]
        
        for i in range(1, len(self.table)):
    
            # Net Requirements
            if self.proj_end_inv[i-1] + self.table['confirmed_order'][i] - self.total_demand[i] <= self.safety_stock:
                self.net_requirements_safety[i] = self.total_demand[i] - self.proj_end_inv[i-1] - self.table['confirmed_order'][i] + self.safety_stock
            else:
                self.net_requirements_safety[i] = 0
            
            # Planned Receipts 
            # IN FUTURE, NEED TO PUT WARNING HERE!!! NO PLANNED RECEIPTS BEFORE LEAD TIME. PUT ORDERS IN CONFIRMED ORDERS.
            if i >= self.sourcing_lead_time: 
                self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.table['confirmed_order'][i] + self.planned_receipts[i] - self.total_demand[i]

        
    def calc(self):
        
        for i in range(0, len(self.table)-int(self.sourcing_lead_time)):
            
            # Planned Orders
            self.planned_orders[i] = self.planned_receipts[i + int(self.sourcing_lead_time)] 
        
        self.table_final = pd.concat([self.table, self.proj_end_inv,self.net_requirements_safety, self.planned_receipts, self.planned_orders],axis=1)
        self.table_final.drop(['confirmed_order'], axis=1, inplace=True)
        self.table_final = json.loads(self.table_final.to_json(orient='records'))
        self.table = json.loads(self.table.to_json())
        self.total_demand = json.loads(self.total_demand.to_json())
        self.net_requirements_safety = json.loads(self.net_requirements_safety.to_json())
        self.planned_orders = json.loads(self.planned_orders.to_json())
        self.proj_end_inv = json.loads(self.proj_end_inv.to_json())
        self.planned_receipts = json.loads(self.planned_receipts.to_json())
        
        return self.planned_orders