# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 12:06:29 2020

@author: James Ang
"""

import json
import math
import copy
import pandas as pd

class Hospital:
    
    def __init__(self, data):
        
        self.data = data
        self.supplier_leadtime = 0 #HardCode
        self.truck_size = 10 #HardCode - boxes
        self.name = self.data.get('name')        
        self.table = pd.DataFrame(self.data.get('daily_consumption_plan'))
        self.table.index = self.table.day
        # self.table.drop('day', axis=1, inplace=True)
        # self.consumption = self.table.iloc[:,1]
        self.hosp_consumption=self.table.loc[:,'consumption']
        self.outbound=self.table.loc[:,'outbound']
        self.consumption = self.hosp_consumption +self.outbound
        
        self.proj_end_inv = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.proj_end_inv_initial = pd.Series(data=[0]*len(self.table), index = self.table.index, name='proj_end_inv_initial')
        self.proj_end_inv_final = pd.Series(data=[0]*len(self.table), index = self.table.index, name='proj_end_inv_final')
        
        self.replenishment_initial = pd.Series(data=[0]*len(self.table), index = self.table.index, name='replenishment_initial')
        self.replenishment_final = pd.Series(data=[0]*len(self.table), index = self.table.index, name='replenishment_final')
        
        self.planned_receipts = pd.Series(data=[0]*len(self.table), index = self.table.index)
        
        self.truck_count = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.truck_count_initial = pd.Series(data=[0]*len(self.table), index = self.table.index, name='truck_count_initial')
        self.truck_count_final = pd.Series(data=[0]*len(self.table), index = self.table.index, name='truck_count_final')
        
        self.supply_lotsize = self.data.get('po_quantity')
        self.safety_stock = self.data.get('safety_stock')
        self.max_inv = self.data.get('maximum_inventory')
        self.iei = self.data.get('initial_ending_inventory')
        
        self.planned_orders = pd.Series(data=[0]*len(self.table), index = self.table.index)
        # self.planned_orders_initial = pd.Series(data=[0]*len(self.table), index = self.table.index) 
        
        self.net_requirements_safety = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.inv_minus_mininv = pd.Series(data=[0]*len(self.table), index = self.table.index)
        
        # INITIALISATIONS
        
        # Net Requirements            
        if self.iei - self.consumption[0] <= self.safety_stock:
            self.net_requirements_safety[0] = self.consumption[0] - self.iei + self.safety_stock
        else:
            self.net_requirements_safety[0] = 0
            
        # Planned Receipts
        self.planned_receipts[0] = math.ceil(self.net_requirements_safety[0]/self.supply_lotsize)*self.supply_lotsize
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.planned_receipts[0] - self.consumption[0]
        
        for i in range(1, len(self.table)):
    
            # Net Requirements
            if self.proj_end_inv[i-1] - self.consumption[i] <= self.safety_stock:
                self.net_requirements_safety[i] = self.consumption[i] - self.proj_end_inv[i-1] + self.safety_stock
            else:
                self.net_requirements_safety[i] = 0
            
            # Planned Receipts
            if i >= self.supplier_leadtime:
                self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.consumption[i]
            
        self.proj_end_inv_initial = copy.deepcopy(self.proj_end_inv)
        self.proj_end_inv_initial.name = "proj_end_inv_initial"
        self.replenishment_initial = copy.deepcopy(self.planned_receipts)
        self.replenishment_initial.name = "replenishment_initial"
        self.proj_end_inv_final = copy.deepcopy(self.proj_end_inv)
        self.proj_end_inv_final.name = "proj_end_inv_final"
        
        

        self.replenishment_final = copy.deepcopy(self.planned_receipts)
        self.replenishment_final.name = "replenishment_final"
        
    # def calc(self):
        
        for i in range(0, len(self.table)-int(self.supplier_leadtime)):
            
            # Planned Orders
            self.planned_orders[i] = self.planned_receipts[i + int(self.supplier_leadtime)] 
            
            # Count trucks
            if self.planned_orders[i] > 0:
                if self.planned_orders[i] <= self.truck_size:
                    self.truck_count[i] = 1
                elif self.planned_orders[i] <= 2*self.truck_size:
                    self.truck_count[i] = 2
                else:
                    pass
            else:
                self.truck_count[i] = 0
        
        self.truck_count_initial = copy.deepcopy(self.truck_count)
        self.truck_count_initial.name = "truck_count_initial"
        self.inv_minus_mininv = self.proj_end_inv-self.safety_stock
        self.truck_count_final = copy.deepcopy(self.truck_count)
        self.truck_count_final.name = "truck_count_final"
        
        
        # return self.planned_orders, self.truck_count
    
    def calc_scen_1(self, troubled_index, prob_type):
        print(f"Problem Type = {prob_type}")        
        
        # Planned Receipts
        if prob_type == 1:
            i = troubled_index-1
            self.planned_receipts[i] = self.supply_lotsize #math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
        elif prob_type == 2:
            i = troubled_index
            self.planned_receipts[i] = 0
        else:
            pass        
        
        # Projected Ending Inventory
        self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.consumption[i]
        
        if prob_type == 2:
            troubled_index = troubled_index +1
        
        for i in range(troubled_index, len(self.table)):
    
            # Net Requirements
            if self.proj_end_inv[i-1] - self.consumption[i] <= self.safety_stock:
                self.net_requirements_safety[i] = self.consumption[i] - self.proj_end_inv[i-1] + self.safety_stock
            else:
                self.net_requirements_safety[i] = 0
            
            # Planned Receipts
            if i >= self.supplier_leadtime:
                self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.consumption[i]
        
        for i in range(0, len(self.table)-int(self.supplier_leadtime)):
            
            # Planned Orders
            self.planned_orders[i] = self.planned_receipts[i + int(self.supplier_leadtime)] 
            
            # Count trucks
            if self.planned_orders[i] > 0:
                if self.planned_orders[i] <= self.truck_size:
                    self.truck_count[i] = 1
                elif self.planned_orders[i] <= 2*self.truck_size:
                    self.truck_count[i] = 2
                else:
                    pass
            else:
                self.truck_count[i] = 0
        
        self.inv_minus_mininv = self.proj_end_inv-self.safety_stock
        
        self.truck_count_final = copy.deepcopy(self.truck_count)
        self.truck_count_final.name = "truck_count_final"
        self.proj_end_inv_final = copy.deepcopy(self.proj_end_inv)
        self.proj_end_inv_final.name = "proj_end_inv_final"
        self.replenishment_final = copy.deepcopy(self.planned_receipts)
        self.replenishment_final.name = "replenishment_final"
        
        return self.planned_orders, self.truck_count
    
    def calc_scen_2(self, troubled_index, prob_type):
        print(f"Problem Type = {prob_type}")        
        
        # Planned Receipts
        if prob_type == 1:
            i = troubled_index-1
            self.planned_receipts[i] = self.supply_lotsize #math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
        elif prob_type == 2:
            i = troubled_index
            self.planned_receipts[i] = 0
        else:
            pass        
        
        # Projected Ending Inventory
        self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.consumption[i]
        
        if prob_type == 2:
            troubled_index = troubled_index +1
        
        for i in range(troubled_index, len(self.table)):
    
            # Net Requirements
            if self.proj_end_inv[i-1] - self.consumption[i] <= self.safety_stock:
                self.net_requirements_safety[i] = self.consumption[i] - self.proj_end_inv[i-1] + self.safety_stock
            else:
                self.net_requirements_safety[i] = 0
            
            # Planned Receipts
            if i >= self.supplier_leadtime:
                self.planned_receipts[i] = math.ceil(self.net_requirements_safety[i]/self.supply_lotsize)*self.supply_lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.consumption[i]
        
        for i in range(0, len(self.table)-int(self.supplier_leadtime)):
            
            # Planned Orders
            self.planned_orders[i] = self.planned_receipts[i + int(self.supplier_leadtime)] 
            
            # Count trucks
            if self.planned_orders[i] > 0:
                if self.planned_orders[i] <= self.truck_size:
                    self.truck_count[i] = 1
                elif self.planned_orders[i] <= 2*self.truck_size:
                    self.truck_count[i] = 2
                else:
                    pass
            else:
                self.truck_count[i] = 0
        
        self.inv_minus_mininv = self.proj_end_inv-self.safety_stock
        
        self.truck_count_final = copy.deepcopy(self.truck_count)
        self.truck_count_final.name = "truck_count_final"
        self.proj_end_inv_final = copy.deepcopy(self.proj_end_inv)
        self.proj_end_inv_final.name = "proj_end_inv_final"
        self.replenishment_final = copy.deepcopy(self.planned_receipts)
        self.replenishment_final.name = "replenishment_final"
        
        return self.planned_orders, self.truck_count
    
    def normalise(self):
        self.table_final = pd.concat([
            self.table,
            self.truck_count_initial, 
            self.proj_end_inv_initial,
            self.replenishment_initial,
            self.truck_count_final, 
            self.proj_end_inv_final, 
            self.replenishment_final
            ],axis=1)
        self.table_final.drop(['consumption'], axis=1, inplace=True)
        self.table_final = json.loads(self.table_final.to_json(orient='records'))
        
        self.table = json.loads(self.table.to_json())
        self.consumption = json.loads(self.consumption.to_json())
        self.net_requirements_safety = json.loads(self.net_requirements_safety.to_json())
        self.planned_orders = json.loads(self.planned_orders.to_json())
        self.proj_end_inv = json.loads(self.proj_end_inv.to_json())
        self.proj_end_inv_initial = json.loads(self.proj_end_inv_initial.to_json())
        self.proj_end_inv_final = json.loads(self.proj_end_inv_final.to_json())
        self.planned_receipts = json.loads(self.planned_receipts.to_json())
        self.inv_minus_mininv = json.loads(self.inv_minus_mininv.to_json())
        self.replenishment_initial = json.loads(self.replenishment_initial.to_json())
        self.replenishment_final = json.loads(self.replenishment_final.to_json())
        self.truck_count = json.loads(self.truck_count.to_json())
        self.truck_count_initial = json.loads(self.truck_count_initial.to_json())
        self.truck_count_final = json.loads(self.truck_count_final.to_json())
                
class Truck:
    
    def __init__(self, data_truck):
        
        # self.num_of_trucks = len(data_truck)
        # self.data = data_truck
        self.name = data_truck.get('name')
        self.truck_type = data_truck.get('truck_type')
        self.current_location = data_truck.get('current_location')
        self.min_lotsize = data_truck.get('min_lotsize')
        self.max_lotsize = data_truck.get('max_lotsize')
        self.max_daily_delivery_hours = data_truck.get('max_daily_delivery_hours')
        
        
        
class Supplier:
    
    def __init__(self, data, hospitals_all, trucks_all):
        
        
        self.df_order = pd.concat([hosp.planned_orders for hosp in hospitals_all], axis=1)

        self.hosp_names = [hosp.name for hosp in hospitals_all]        
        
        truck_list = [data.truck_count for data in hospitals_all]        
        
        self.df_truck = pd.concat(truck_list, axis=1)
        
        self.num_of_trucks = len(trucks_all)
        
        # Supplier
        supplier_demand = self.df_order.sum(axis=1)
        total_truck_count = self.df_truck.sum(axis=1)
        
        # Assign trucks
        df_truck_cum_sum = self.df_truck.cumsum(axis=1)
        for i in reversed(range(1,len(hospitals_all))):
        
            a = df_truck_cum_sum.iloc[:,i] == df_truck_cum_sum.iloc[:,i-1]
            df_truck_cum_sum.iloc[:,i][a] = 0
        
        truck_available = [data.name for data in trucks_all]
        
        self.truck_name = []
        for i in range(0,len(hospitals_all)):
            if i<len(truck_available):
                self.truck_name.append(truck_available[i])
            else:
                self.truck_name.append('Unavailable')
                
        hospital_names = [data.name for data in hospitals_all]
        
        truck_schedule_initial = df_truck_cum_sum.replace(list(range(1, len(hospitals_all)+1)),self.truck_name)
        
        truck_schedule_initial.columns = self.hosp_names
        
        
        
        
        self.data = data[0]
    #     # self.hosp_num = hosp_num
        self.name = self.data.get('name')        
        self.table = pd.DataFrame(self.data.get('daily_replenishment_after_quarantine'))
        self.table.index = self.table.day
        # self.table.drop('day', axis=1, inplace=True)
        self.total_demand = supplier_demand
        self.total_demand_final = pd.Series(data=[0]*len(self.table), index = self.table.index)

        self.proj_end_inv = pd.Series(data=[0]*len(self.table), index = self.table.index)
        # self.planned_receipts = pd.Series(data=[0]*len(self.table), index = self.table.index)
        # self.planned_receipts = self.table.iloc[:,1]
        self.planned_receipts = self.table.loc[:,'quantity']
        
        self.total_truck_count_initial = total_truck_count
        self.total_truck_count_initial.name = "total_truck_count_initial"
        
        self.truck_schedule_initial = truck_schedule_initial
        self.truck_schedule_initial.name = "truck_schedule_initial"
        # self.supply_quarantine = self.table.iloc[:,0]
        # self.quarantine_lead_time = 0
        
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
        
        # DC INITIALISATIONS

        # # Planned Receipts
        # for i in range(0, len(self.table)-int(self.quarantine_lead_time)):
            
        #     self.planned_receipts[i+int(self.quarantine_lead_time)] = self.supply_quarantine[i]
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.planned_receipts[0] - self.total_demand[0]
        
        for i in range(1, len(self.table)):
    

            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.total_demand[i]
        
        self.total_demand_initial = copy.deepcopy(self.total_demand)
        self.total_demand_initial.name = "total_demand_initial"
        self.proj_end_inv_initial = copy.deepcopy(self.proj_end_inv)
        self.proj_end_inv_initial.name = "proj_end_inv_initial"
            
    def calc(self, data, supplier_demand_new, total_truck_count,truck_schedule_final):
        # self.data = data
    #     # self.hosp_num = hosp_num
        # self.name = self.data.get('name')        
        # self.table = pd.DataFrame(self.data.get('daily_replenishment_after_quarantine'))
        # self.table.index = self.table.day
        # self.table.drop('day', axis=1, inplace=True)
        self.total_demand = supplier_demand_new
        self.planned_receipts = pd.Series(data=[0]*len(self.table), index = self.table.index)
        # self.supply_after_quarantine = self.table.iloc[:,1]
        self.supply_after_quarantine = self.table.loc[:,'quantity']
        
        self.quarantine_lead_time = 0
        self.total_truck_count_final = total_truck_count
        self.total_truck_count_final.name = "total_truck_count_final"
        self.truck_schedule_final = truck_schedule_final
        self.truck_schedule_final.name = "truck_schedule_final"
        # self.truck_schedule_final = self.truck_schedule_final.rename(columns={'0': 'newName1', '1': 'newName2', '2': 'newName3'})
        
    # # Convert days to weeks
    #     if self.data.get('quarantine_lead_time')<7:
    #         self.quarantine_lead_time  = 0
    #     elif self.data.get('quarantine_lead_time')<14:
    #         self.quarantine_lead_time  = 1
    #     elif self.data.get('quarantine_lead_time')<21:
    #         self.quarantine_lead_time  = 2
    #     else:
    #         pass       

        # self.safety_stock = self.data.get('safety_stock')
        # self.max_inv = self.data.get('maximum_inventory')
        # self.iei = self.data.get('initial_ending_inventory')
        
        # DC INITIALISATIONS

        # Planned Receipts
        for i in range(0, len(self.table)-int(self.quarantine_lead_time)):
            
            self.planned_receipts[i+int(self.quarantine_lead_time)] = self.supply_after_quarantine[i]
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = self.iei + self.planned_receipts[0] - self.total_demand[0]
        
        for i in range(1, len(self.table)):
    

            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.planned_receipts[i] - self.total_demand[i]
        
        self.total_demand_final = copy.deepcopy(self.total_demand)
        self.total_demand_final.name = "total_demand_final "
        self.proj_end_inv_final = copy.deepcopy(self.proj_end_inv)
        self.proj_end_inv_final.name = "proj_end_inv_final"
        
    def normalise(self):
        self.table_final = pd.concat([
            self.table,
            self.total_truck_count_initial,
            self.total_demand_initial,
            self.proj_end_inv_initial,
            # self.truck_schedule_initial,
            self.total_truck_count_final,
            self.total_demand_final, 
            self.proj_end_inv_final,
            # self.truck_schedule_final,
            # self.replenishment_final
            ],axis=1)
        self.table_final.drop(['quantity'], axis=1, inplace=True)
        self.table_final = json.loads(self.table_final.to_json(orient='records'))
        
        self.truck_sched_initial = pd.concat([self.table,self.truck_schedule_initial],axis=1)
        self.truck_sched_initial.drop(['quantity'], axis=1, inplace=True)        
        self.truck_sched_initial = json.loads(self.truck_sched_initial.to_json(orient='records'))
        
        self.truck_sched_final = pd.concat([self.table,self.truck_schedule_final],axis=1)
        self.truck_sched_final.drop(['quantity'], axis=1, inplace=True)        
        self.truck_sched_final = json.loads(self.truck_sched_final.to_json(orient='records'))
        # self.truck_schedule_final = json.loads(self.truck_schedule_final.to_json(orient='records'))
        
        self.table = json.loads(self.table.to_json())
        self.supply_after_quarantine = json.loads(self.supply_after_quarantine.to_json())
        # self.net_requirements_safety = json.loads(self.net_requirements_safety.to_json())
        # self.planned_orders = json.loads(self.planned_orders.to_json())
        self.proj_end_inv = json.loads(self.proj_end_inv.to_json())
        self.proj_end_inv_initial = json.loads(self.proj_end_inv_initial.to_json())
        self.proj_end_inv_final = json.loads(self.proj_end_inv_final.to_json())
        self.planned_receipts = json.loads(self.planned_receipts.to_json())
        # self.inv_minus_mininv = json.loads(self.inv_minus_mininv.to_json())
        # self.replenishment_initial = json.loads(self.replenishment_initial.to_json())
        # self.replenishment_final = json.loads(self.replenishment_final.to_json())
        self.total_truck_count_initial = json.loads(self.total_truck_count_initial.to_json())
        self.total_truck_count_final = json.loads(self.total_truck_count_final.to_json())
        self.total_demand = json.loads(self.total_demand.to_json())
        self.total_demand_initial = json.loads(self.total_demand_initial.to_json())
        self.total_demand_final = json.loads(self.total_demand_final.to_json())
        
        
def truck_stat(total_truck_count,num_of_trucks):
    troubled_truck_index = total_truck_count[total_truck_count > num_of_trucks].index
    
     # in integer
    
    if len(troubled_truck_index) == 0:
        truck_status = "OK"
        print(f"Truck status original: {truck_status}")
        troubled_truck_index_int = math.nan
    else:
        truck_status = "NG"
        troubled_truck_index_int = total_truck_count.index.get_loc(troubled_truck_index[0])
        print(f"Truck status original: {truck_status} at {troubled_truck_index_int}")
        
    return troubled_truck_index_int, truck_status

def supp_inv_stat(proj_end_inv):
    
    sup_proj_EI_initial = pd.Series(proj_end_inv)
    troubled_sup_inv_value = sup_proj_EI_initial[sup_proj_EI_initial<0]
    troubled_sup_inv_index = sup_proj_EI_initial[sup_proj_EI_initial<0].index
    
    
    if len(troubled_sup_inv_index) == 0:
        sup_inv_status = "OK"
        print(f"Supplier Inv status original: {sup_inv_status}")
        troubled_sup_inv_index_int = 0
    else:
        sup_inv_status = "NG"
        troubled_sup_inv_index_int = sup_proj_EI_initial.index.get_loc(troubled_sup_inv_index[0]) # in integer
        print(f"Supplier Inv status original: {sup_inv_status} at {troubled_sup_inv_index_int}")

    return troubled_sup_inv_value,troubled_sup_inv_index_int, sup_inv_status
