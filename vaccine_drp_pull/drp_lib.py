# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 18:13:24 2020

@author: James Ang
"""

import pandas as pd
import math

class Demand_Centre:
    
    # CLASS ATTRIBUTES
    
    # INSTANCE ATTRIBUTES
    def __init__(self, excelfile, sheet_name):
        
        self.excelfile = excelfile
        self.sheet_name = sheet_name
        self.table = pd.read_excel(self.excelfile, sheet_name=self.sheet_name, skiprows = 11, usecols = 'B:L')
        self.table.index = self.table['Category']
        self.table.drop('Category', axis=1, inplace=True)
        self.table = self.table.transpose().fillna(0)
        self.total_demand = self.table['Spot Forecast Demand(MT)'] +\
                    self.table['Spot Order (MT)'] +\
                    self.table['Term Forecast Demand (MT)'] +\
                    self.table['Term Order (MT)']
        self.product_selling_price = self.table['Product Selling Price (RM/MT)']
        self.spot_forecast_demand = self.table['Spot Forecast Demand(MT)']
        self.spot_order = self.table['Spot Order (MT)']
        self.proj_end_inv = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.planned_receipts = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.net_requirements = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.planned_orders = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.truck_count_10T = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.truck_count_20T = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.total_shipment_cost = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.product_unit_cost = self.table['Product Unit Cost (RM/MT)']
        self.product_cost = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.totalsupply_cost = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.revenue = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.profit = pd.Series(data=[0]*len(self.table), index = self.table.index)
        
        # Spot Variables
        self.spot_demand = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.spot_demand_to_reduce_exact = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.spot_demand_to_reduce_lotsize = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.spot_truck_count_10T = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.spot_truck_count_20T = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.spot_shipment_cost = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.spot_product_cost = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.spot_total_supply_cost = pd.Series(data=[0]*len(self.table), index = self.table.index) 
        self.spot_drop_in_revenue = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.spot_profit_loss = pd.Series(data=[0]*len(self.table), index = self.table.index) 
        self.final_profit = pd.Series(data=[0]*len(self.table), index = self.table.index)
        self.spot_profit_loss_placeholder = pd.Series(data=[0]*len(self.table), index = self.table.index)
        
        self.supplier_selection = ""
        self.supplier_leadtime  = 0
        self.ship10T_val = 0
        self.ship10T_cost = 0
        self.ship20T_val = 0
        self.ship20T_cost = 0
        
    def calculate(self, supplier_params, dc_params): 
        
        # # print(supplier_params)
        # if supplier_params[0].supplier_availability == 'No' and supplier_params[1].supplier_availability == 'No':
        #     print('All Suppliers are not available!')
        
        # else:
            
        if dc_params.ship_cost20T_sup1 < dc_params.ship_cost20T_sup2:
            
            if supplier_params[0].supplier_availability == 'Yes':                

                self.supplier_selection = "Supplier 1"
                self.supplier_leadtime = dc_params.leadtime_sup1
                
                self.ship10T_val = dc_params.ship_value10T_sup1
                self.ship10T_cost = dc_params.ship_cost10T_sup1
                
                self.ship20T_val = dc_params.ship_value20T_sup1
                self.ship20T_cost = dc_params.ship_cost20T_sup1
            
            elif supplier_params[0].supplier_availability == 'No':
                
                self.supplier_selection = "Supplier 2"
                self.supplier_leadtime = dc_params.leadtime_sup2
                
                self.ship10T_val = dc_params.ship_value10T_sup2
                self.ship10T_cost = dc_params.ship_cost10T_sup2
                
                self.ship20T_val = dc_params.ship_value20T_sup2
                self.ship20T_cost = dc_params.ship_cost20T_sup2
            
            else:
                pass
            
        else:
            
            if supplier_params[1].supplier_availability == 'Yes':
                
                self.supplier_selection = "Supplier 2"
                self.supplier_leadtime = dc_params.leadtime_sup2
                
                self.ship10T_val = dc_params.ship_value10T_sup2
                self.ship10T_cost = dc_params.ship_cost10T_sup2
                
                self.ship20T_val = dc_params.ship_value20T_sup2
                self.ship20T_cost = dc_params.ship_cost20T_sup2
                
            else:
                
                self.supplier_selection = "Supplier 1"
                self.supplier_leadtime = dc_params.leadtime_sup1
                
                self.ship10T_val = dc_params.ship_value10T_sup1
                self.ship10T_cost = dc_params.ship_cost10T_sup1
                
                self.ship20T_val = dc_params.ship_value20T_sup1
                self.ship20T_cost = dc_params.ship_cost20T_sup1
    
    
        # DC INITIALISATIONS
        
        # Net Requirements            
        if dc_params.init_end_inv + self.table['Scheduled Receipts (MT)'][0] - self.total_demand[0] <= dc_params.safety_stock:
            self.net_requirements[0] = self.total_demand[0] - dc_params.init_end_inv - self.table['Scheduled Receipts (MT)'][0] + dc_params.safety_stock
        else:
            self.net_requirements[0] = 0
        
        # Planned Receipts
        self.planned_receipts[0] = math.ceil(self.net_requirements[0]/dc_params.lotsize)*dc_params.lotsize
        
        # Projected Ending Inventory
        self.proj_end_inv[0] = dc_params.init_end_inv + self.table['Scheduled Receipts (MT)'][0] + self.planned_receipts[0] - self.total_demand[0]

        
        
        for i in range(1, len(self.table)):
    
            # Net Requirements
            if self.proj_end_inv[i-1] + self.table['Scheduled Receipts (MT)'][i] - self.total_demand[i] <= dc_params.safety_stock:
                self.net_requirements[i] = self.total_demand[i] - self.proj_end_inv[i-1] - self.table['Scheduled Receipts (MT)'][i] + dc_params.safety_stock
            else:
                self.net_requirements[i] = 0
            
            # Planned Receipts
            if i >= self.supplier_leadtime:
                self.planned_receipts[i] = math.ceil(self.net_requirements[i]/dc_params.lotsize)*dc_params.lotsize
            
            # Projected Ending Inventory
            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.table['Scheduled Receipts (MT)'][i] + self.planned_receipts[i] - self.total_demand[i]

        for i in range(0, len(self.table)-int(self.supplier_leadtime)):
            
            # Planned Orders
            self.planned_orders[i] = self.planned_receipts[i + int(self.supplier_leadtime)]        

            # Adding truck count
            self.truck_count_10T[i] = ((self.planned_orders[i] + self.ship10T_val - 1)%self.ship20T_val)//self.ship10T_val
            self.truck_count_20T[i] = (self.planned_orders[i] + self.ship10T_val - 1)//self.ship20T_val
            
            # Total Transportation Cost
            self.total_shipment_cost[i] = self.truck_count_10T[i]*self.ship10T_cost + self.truck_count_20T[i]*self.ship20T_cost
            
            # Product Cost
            self.product_cost[i] = self.product_unit_cost[i]*self.planned_orders[i]
            
            # Total Supply Cost
            self.totalsupply_cost[i] = self.total_shipment_cost[i] + self.product_cost[i]
            
            # Revenue
            self.revenue[i] = self.product_selling_price[i]*self.planned_orders[i]
            
            # Profit
            self.profit[i] = self.revenue[i] - self.totalsupply_cost[i]
            
            # Spot Demand
            self.spot_demand[i] = self.spot_forecast_demand[i + int(self.supplier_leadtime)] + self.spot_order[i + int(self.supplier_leadtime)]
        
        return self.proj_end_inv, self.planned_receipts, self.net_requirements


class Demand_Centre_Params:
    
    # INSTANCE ATTRIBUTES
    def __init__(self, excelfile, sheet_name): 
        
        self.excelfile = excelfile
        self.sheet_name = sheet_name
        self.table = pd.read_excel(self.excelfile, sheet_name = self.sheet_name, skiprows = 1, nrows = 9, usecols = 'B:D')
        self.table.index = self.table['Category']
        self.table.drop('Category', axis=1, inplace=True)
        self.table = self.table.transpose().fillna(0)
        self.init_end_inv = self.table.loc['Value','Initial Ending Inventory (MT)']
        self.safety_stock = self.table.loc['Value','Safety Stock (MT)']
        self.leadtime_sup1 = self.table.loc['Value','Delivery Lead Time (weeks) - sup 1']
        self.leadtime_sup2 = self.table.loc['Value','Delivery Lead Time (weeks) - sup 2']
        self.lotsize = self.table.loc['Value','Lot Size (MT)']
        self.ship_value10T_sup1 = self.table.loc['Value','Shipment cost (10 Ton) - sup 1']
        self.ship_value20T_sup1 = self.table.loc['Value','Shipment cost (20 Ton) - sup 1']
        self.ship_value10T_sup2 = self.table.loc['Value','Shipment cost (10 Ton) - sup 2']
        self.ship_value20T_sup2 = self.table.loc['Value','Shipment cost (20 Ton) - sup 2']        
        self.ship_cost10T_sup1 = self.table.loc['Price','Shipment cost (10 Ton) - sup 1']
        self.ship_cost20T_sup1 = self.table.loc['Price','Shipment cost (20 Ton) - sup 1']
        self.ship_cost10T_sup2 = self.table.loc['Price','Shipment cost (10 Ton) - sup 2']
        self.ship_cost20T_sup2 = self.table.loc['Price','Shipment cost (20 Ton) - sup 2']
        
class Supplier_Params:
    
    # INSTANCE ATTRIBUTES
    
    def __init__(self, excelfile, sheet_name):
        
        self.excelfile = excelfile
        self.sheet_name = sheet_name
        self.table = pd.read_excel(self.excelfile, sheet_name = self.sheet_name, skiprows = 2, nrows= 8, usecols = 'B:C')
        self.table.index = self.table['Category']
        self.table.drop('Category', axis=1, inplace=True)
        self.table = self.table.transpose().fillna(0)
        self.init_end_inv = self.table.loc['Value','Initial Ending Inventory (MT)']
        self.safety_stock = self.table.loc['Value','Safety Stock (MT)']
        self.lotsize = self.table.loc['Value','Lot Size (MT)']
        self.method = self.table.loc['Value','Method']
        self.production_leadtime = self.table.loc['Value','Production Lead Time (weeks)']
        self.max_weekly_production = self.table.loc['Value','Max Weekly Production']
        self.supplier_availability = self.table.loc['Value','Supplier Availability']
        
        if self.supplier_availability == "Yes":
            print(sheet_name + ' is Available.')
        elif self.supplier_availability == "No":
            print(sheet_name + ' is not Available.')
        else:
            pass
        
        print(f"{self.sheet_name} - '{self.method}' selected.\n")
        
# class Supplier:

#     def __init__(self, supplier_params, supp_num, demand_centres):
        
#         self.respective_dc_demands = []        
        
#         for i in range (0,len(demand_centres)):
#             # print(demand_centres[i].supplier_selection)
            
#             if demand_centres[i].supplier_selection == supp_num:
#                 # print(supplier_params.supplier_availability)
                
#                 if supplier_params.supplier_availability == 'Yes':                    
#                     self.respective_dc_demands.append(demand_centres[i].planned_orders)
            
#                 else:                    
#                     self.respective_dc_demands.append(pd.Series(data=[0]*len(demand_centres[0].planned_orders), index = demand_centres[0].planned_orders.index))
            
#             else:                
#                 self.respective_dc_demands.append(pd.Series(data=[0]*len(demand_centres[0].planned_orders), index = demand_centres[0].planned_orders.index))
        
#         self.forecast_demand = sum(self.respective_dc_demands)

#         self.proj_end_inv = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
#         self.net_requirements = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
#         self.planned_orders = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
#         self.master_production_schedule = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
#         self.qty_to_move = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
#         self.qty_to_reduce = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
            
#     #%% INITIALISATIONS, i = 0
#     def calculate(self, supplier_params):
        
#         # Initial Net Requirements
#         if supplier_params.init_end_inv - self.forecast_demand[0] <= supplier_params.safety_stock:
#             self.net_requirements[0] = self.forecast_demand[0] - supplier_params.init_end_inv + supplier_params.safety_stock
        
#         else:
#             self.net_requirements[0] = 0
            
#         # Initial Master Production Schedule
#         self.master_production_schedule[0] = math.ceil(self.net_requirements[0]/supplier_params.lotsize)*supplier_params.lotsize
        
#         # Initial Project Ending Inventory
#         self.proj_end_inv[0] = supplier_params.init_end_inv +\
#                                 self.master_production_schedule[0] -\
#                                 self.forecast_demand[0]
        
#         #%% CALCULATIONS, i > 0
#         for i in range(1, len(self.forecast_demand)):
        
#             # Net Requirements        
#             if self.proj_end_inv[i-1] - self.forecast_demand[i] <= supplier_params.safety_stock:
#                 self.net_requirements[i] = self.forecast_demand[i] - self.proj_end_inv[i-1] + supplier_params.safety_stock
                
#             else:
#                 self.net_requirements[i] = 0
            
#             # Master Production Schedule        
#             if i >= supplier_params.production_leadtime:
#                 self.master_production_schedule[i] = math.ceil(self.net_requirements[i]/supplier_params.lotsize)*supplier_params.lotsize
#                 # self.updated_MPS[i] = self.master_production_schedule[i]
            
#             # Projected Ending Inventory        
#             self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.master_production_schedule[i] - self.forecast_demand[i]

#         for i in range(0, len(self.forecast_demand)-int(supplier_params.production_leadtime)):
        
#             # Planned Orders
#             self.planned_orders[i] = self.master_production_schedule[i + int(supplier_params.production_leadtime)]
            
#             # Supplier Amount to Reduce
#             if self.net_requirements[i] - supplier_params.max_weekly_production >=0:
                
#                 # Spot Quantity to Reduce
#                 self.qty_to_reduce[i] = self.net_requirements[i] - supplier_params.max_weekly_production
                
#                 # Amount to Move
#                 self.qty_to_move[i] = self.master_production_schedule[i] - supplier_params.max_weekly_production
#             else:
#                 self.qty_to_reduce[i] = 0
#                 self.qty_to_move[i] = 0

class Supplier:
    
    def __init__(self, supplier_params, supp_num, demand_centres):
        
        self.respective_dc_demands = []
        self.supp_num = supp_num
        
        for i in range (0,len(demand_centres)):
            # print(demand_centres[i].supplier_selection)
            
            if demand_centres[i].supplier_selection == self.supp_num:
                # print(supplier_params.supplier_availability)
                
                if supplier_params.supplier_availability == 'Yes':                    
                    self.respective_dc_demands.append(demand_centres[i].planned_orders)
            
                else:                    
                    self.respective_dc_demands.append(pd.Series(data=[0]*len(demand_centres[0].planned_orders), index = demand_centres[0].planned_orders.index))
            
            else:
                self.respective_dc_demands.append(pd.Series(data=[0]*len(demand_centres[0].planned_orders), index = demand_centres[0].planned_orders.index))
        
        self.forecast_demand = sum(self.respective_dc_demands)
        self.proj_end_inv = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.net_requirements = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.planned_orders = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.master_production_schedule = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.qty_to_move = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.qty_to_reduce = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
            
    #%% INITIALISATIONS, i = 0
    def calculate(self, supplier_params, demand_centres, dc_params):
        
        # Initial Net Requirements
        if supplier_params.init_end_inv - self.forecast_demand[0] <= supplier_params.safety_stock:
            self.net_requirements[0] = self.forecast_demand[0] - supplier_params.init_end_inv + supplier_params.safety_stock
        
        else:
            self.net_requirements[0] = 0
            
        # Initial Master Production Schedule
        self.master_production_schedule[0] = math.ceil(self.net_requirements[0]/supplier_params.lotsize)*supplier_params.lotsize
        
        # Initial Project Ending Inventory
        self.proj_end_inv[0] = supplier_params.init_end_inv +\
                                self.master_production_schedule[0] -\
                                self.forecast_demand[0]
        
        #%% CALCULATIONS, i > 0
        
        for i in range(0, len(self.forecast_demand)):

            if i > 0:
            # Start with i=1 because PEI starts    i-1
            # i=0 has been calculated during Initialisation
            # Don't need i= 0 because already initialised earlier             
                    
                # Net Requirements
                if self.proj_end_inv[i-1] - self.forecast_demand[i] <= supplier_params.safety_stock:
                    self.net_requirements[i] = self.forecast_demand[i] - self.proj_end_inv[i-1] + supplier_params.safety_stock
                    
                else:
                    self.net_requirements[i] = 0
                
                # Master Production Schedule        
                if i >= supplier_params.production_leadtime:
                    self.master_production_schedule[i] = math.ceil(self.net_requirements[i]/supplier_params.lotsize)*supplier_params.lotsize
                    # self.updated_MPS[i] = self.master_production_schedule[i]
            
                # Projected Ending Inventory        
                self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.master_production_schedule[i] - self.forecast_demand[i]

            if i >= int(supplier_params.production_leadtime):
                
                # Planned Orders - can only be calculated backwards after leadtime has passed
                self.planned_orders[i - int(supplier_params.production_leadtime)] = self.master_production_schedule[i]

            if i < len(self.forecast_demand)-int(supplier_params.production_leadtime):
                                                    
                # Supplier Amount to Reduce
                if self.net_requirements[i] - supplier_params.max_weekly_production >=0:
                    
                    # Spot Quantity to Reduce
                    self.qty_to_reduce[i] = self.net_requirements[i] - supplier_params.max_weekly_production
                    
                    # Amount to Move
                    self.qty_to_move[i] = self.master_production_schedule[i] - supplier_params.max_weekly_production
                else:
                    self.qty_to_reduce[i] = 0
                    self.qty_to_move[i] = 0


        #%% CALCULATIONS
        
            if supplier_params.method == 'Reduce Spot Demand':                
            
                for dc_num in range(0,len(demand_centres)):
                    
                    if demand_centres[dc_num].supplier_selection == self.supp_num:
                    
                        if i < len(demand_centres[dc_num].table) - demand_centres[dc_num].supplier_leadtime:
                            
                            # Spot Demand to Reduce - lotsize
                            demand_centres[dc_num].spot_demand_to_reduce_lotsize[i] = \
                                min(max(math.ceil(self.qty_to_reduce[i]/dc_params[dc_num].lotsize)*dc_params[dc_num].lotsize, 0), \
                                demand_centres[dc_num].spot_demand[i])
                            
                            # Spot Demand to Reduce - exact
                            demand_centres[dc_num].spot_demand_to_reduce_exact[i] = \
                                min(max(math.ceil(self.qty_to_reduce[i]/dc_params[dc_num].lotsize)*dc_params[dc_num].lotsize \
                                - (demand_centres[dc_num].planned_receipts[i + int(demand_centres[dc_num].supplier_leadtime)] \
                                - demand_centres[dc_num].net_requirements[i + int(demand_centres[dc_num].supplier_leadtime)]),0), \
                                demand_centres[dc_num].spot_demand[i])
                                    
                        # Spot truck count - DC1
                        demand_centres[dc_num].spot_truck_count_10T[i] = \
                            ((demand_centres[dc_num].spot_demand_to_reduce_exact[i] + demand_centres[dc_num].ship10T_val - 1)%demand_centres[dc_num].ship20T_val)//demand_centres[dc_num].ship10T_val
                        
                        demand_centres[dc_num].spot_truck_count_20T[i] = \
                            (demand_centres[dc_num].spot_demand_to_reduce_exact[i] + demand_centres[dc_num].ship10T_val - 1)//demand_centres[dc_num].ship20T_val
                        
                        # Spot Transportation cost - DC1, DC2, DC3
                        demand_centres[dc_num].spot_shipment_cost[i] = \
                            demand_centres[dc_num].spot_truck_count_10T[i]*demand_centres[dc_num].ship10T_cost \
                            + demand_centres[dc_num].spot_truck_count_20T[i]*demand_centres[dc_num].ship20T_cost
                        
                        # Spot Product Cost
                        demand_centres[dc_num].spot_product_cost[i] = \
                            demand_centres[dc_num].product_unit_cost[i]*demand_centres[dc_num].spot_demand_to_reduce_exact[i]
                        
                        # Spot Total Supply Cost
                        demand_centres[dc_num].spot_total_supply_cost[i] = \
                            demand_centres[dc_num].spot_shipment_cost[i] + demand_centres[dc_num].spot_product_cost[i]
                        
                        # Spot Drop in Revenue
                        demand_centres[dc_num].spot_drop_in_revenue[i] = \
                            demand_centres[dc_num].product_selling_price[i]*demand_centres[dc_num].spot_demand_to_reduce_exact[i]
                        
                        # Spot Profit Loss
                        demand_centres[dc_num].spot_profit_loss[i] = \
                            demand_centres[dc_num].spot_drop_in_revenue[i] - demand_centres[dc_num].spot_total_supply_cost[i]

                        # Final profit
                        demand_centres[dc_num].final_profit[i] = \
                            demand_centres[dc_num].profit[i] - demand_centres[dc_num].spot_profit_loss[i]
                    

class Optimize_DRP:
    
    def __init__(self, supplier_params, supp_num, demand_centres):
        
        self.respective_dc_demands = []
        self.supp_num = supp_num
        
        for dc_count in range (0,len(demand_centres)):
            # print(demand_centres[dc_count].supplier_selection)
            
            if demand_centres[dc_count].supplier_selection == supp_num:
                # print(supplier_params.supplier_availability)
                
                if supplier_params.supplier_availability == 'Yes':                    
                    self.respective_dc_demands.append(demand_centres[dc_count].planned_orders)
            
                else:                    
                    self.respective_dc_demands.append(pd.Series(data=[0]*len(demand_centres[0].planned_orders), index = demand_centres[0].planned_orders.index))
            
            else:
                self.respective_dc_demands.append(pd.Series(data=[0]*len(demand_centres[0].planned_orders), index = demand_centres[0].planned_orders.index))
        
        self.forecast_demand = sum(self.respective_dc_demands)
        self.proj_end_inv = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.net_requirements = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.planned_orders = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.master_production_schedule = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.qty_to_move = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.qty_to_reduce = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.buffer = 8
        self.min_list = []
        self.status = "Production okay"
        self.min_value = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
        self.min_index = pd.Series(data=[0]*len(self.forecast_demand), index = self.forecast_demand.index)
            
    #%% INITIALISATIONS, i = 0
    def optimize(self, supplier_params, demand_centres, dc_params):
        
        if supplier_params.supplier_availability == "Yes":
            
            print(self.supp_num)
            # Initial Net Requirements
            if supplier_params.init_end_inv - self.forecast_demand[0] <= supplier_params.safety_stock:
                self.net_requirements[0] = self.forecast_demand[0] - supplier_params.init_end_inv + supplier_params.safety_stock
            
            else:
                self.net_requirements[0] = 0
                
            # Initial Master Production Schedule
            self.master_production_schedule[0] = math.ceil(self.net_requirements[0]/supplier_params.lotsize)*supplier_params.lotsize
            
            # Initial Project Ending Inventory
            self.proj_end_inv[0] = supplier_params.init_end_inv +\
                                    self.master_production_schedule[0] -\
                                    self.forecast_demand[0]
            
            #%% CALCULATIONS, i > 0
            
            for i in range(0, len(self.forecast_demand)):
                
                if self.status == "Production maxed out":
                    break
                
                if i > 0:
                # Start with i=1 because PEI starts i-1
                # i=0 has been calculated during Initialisation
                # Don't need i= 0 because already initialised earlier
                        
                    # Net Requirements
                    if self.proj_end_inv[i-1] - self.forecast_demand[i] <= supplier_params.safety_stock:
                        self.net_requirements[i] = self.forecast_demand[i] - self.proj_end_inv[i-1] + supplier_params.safety_stock
                        
                    else:
                        self.net_requirements[i] = 0
                    
                    # Master Production Schedule
                    if i >= supplier_params.production_leadtime:
                        self.master_production_schedule[i] = math.ceil(self.net_requirements[i]/supplier_params.lotsize)*supplier_params.lotsize
                        # self.updated_MPS[i] = self.master_production_schedule[i]
                
                    # Projected Ending Inventory        
                    self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.master_production_schedule[i] - self.forecast_demand[i]
    
                # if i >= int(supplier_params.production_leadtime):
                    
                #     # Planned Orders - can only be calculated backwards after leadtime has passed
                #     self.planned_orders[i - int(supplier_params.production_leadtime)] = self.master_production_schedule[i]
    
                if i < len(self.forecast_demand)-int(supplier_params.production_leadtime):
                                                        
                    # Supplier Amount to Reduce
                    if self.net_requirements[i] - supplier_params.max_weekly_production >=0:
                        
                        # Spot Quantity to Reduce
                        self.qty_to_reduce[i] = self.net_requirements[i] - supplier_params.max_weekly_production
                        
                        # Amount to Move
                        self.qty_to_move[i] = self.master_production_schedule[i] - supplier_params.max_weekly_production
                    else:
                        self.qty_to_reduce[i] = 0
                        self.qty_to_move[i] = 0
    
            #%% CALCULATIONS
            
                if supplier_params.method == 'Reduce Spot Demand':# and                 
                    
                    self.min_list = []
                    
                    # For all demand centres..
                    for dc_num in range(0,len(demand_centres)):
                        # print(dc_num)
                        
                        if demand_centres[dc_num].supplier_selection == self.supp_num:
                        
                            if i < len(demand_centres[dc_num].table) - demand_centres[dc_num].supplier_leadtime:
                                
                                # Spot Demand to Reduce - lotsize
                                demand_centres[dc_num].spot_demand_to_reduce_lotsize[i] = \
                                    min(max(math.ceil(self.qty_to_reduce[i]/dc_params[dc_num].lotsize)*dc_params[dc_num].lotsize, 0), \
                                    demand_centres[dc_num].spot_demand[i])
                                
                                # Spot Demand to Reduce
                                demand_centres[dc_num].spot_demand_to_reduce_exact[i] = \
                                    min(max(math.ceil(self.qty_to_reduce[i]/dc_params[dc_num].lotsize)*dc_params[dc_num].lotsize \
                                    - (demand_centres[dc_num].planned_receipts[i + int(demand_centres[dc_num].supplier_leadtime)] \
                                    - demand_centres[dc_num].net_requirements[i + int(demand_centres[dc_num].supplier_leadtime)]),0), \
                                    demand_centres[dc_num].spot_demand[i])
                                        
                            # Spot truck count - DC1
                            demand_centres[dc_num].spot_truck_count_10T[i] = \
                                ((demand_centres[dc_num].spot_demand_to_reduce_exact[i] + demand_centres[dc_num].ship10T_val - 1)%demand_centres[dc_num].ship20T_val)//demand_centres[dc_num].ship10T_val
                            
                            demand_centres[dc_num].spot_truck_count_20T[i] = \
                                (demand_centres[dc_num].spot_demand_to_reduce_exact[i] + demand_centres[dc_num].ship10T_val - 1)//demand_centres[dc_num].ship20T_val
                            
                            # Spot Transportation cost - DC1, DC2, DC3
                            demand_centres[dc_num].spot_shipment_cost[i] = \
                                demand_centres[dc_num].spot_truck_count_10T[i]*demand_centres[dc_num].ship10T_cost \
                                + demand_centres[dc_num].spot_truck_count_20T[i]*demand_centres[dc_num].ship20T_cost
                            
                            # Spot Product Cost
                            demand_centres[dc_num].spot_product_cost[i] = \
                                demand_centres[dc_num].product_unit_cost[i]*demand_centres[dc_num].spot_demand_to_reduce_exact[i]
                            
                            # Spot Total Supply Cost
                            demand_centres[dc_num].spot_total_supply_cost[i] = \
                                demand_centres[dc_num].spot_shipment_cost[i] + demand_centres[dc_num].spot_product_cost[i]
                            
                            # Spot Drop in Revenue
                            demand_centres[dc_num].spot_drop_in_revenue[i] = \
                                demand_centres[dc_num].product_selling_price[i]*demand_centres[dc_num].spot_demand_to_reduce_exact[i]
                            
                            # Spot Profit Loss
                            demand_centres[dc_num].spot_profit_loss[i] = \
                                demand_centres[dc_num].spot_drop_in_revenue[i] - demand_centres[dc_num].spot_total_supply_cost[i]
    
                            # Final profit
                            demand_centres[dc_num].final_profit[i] = \
                                demand_centres[dc_num].profit[i] - demand_centres[dc_num].spot_profit_loss[i]
    
    #%% OPTIMISATION STARTS HERE
    
                            # Placeholding "Loss in Spot Profit"
                            demand_centres[dc_num].spot_profit_loss_placeholder[i] = demand_centres[dc_num].spot_profit_loss[i]
    
                            # Setting "Loss in Spot Profit" to high value to prevent from being selected during minimisation.
                            if self.qty_to_reduce[i] > 0:
                                if int(demand_centres[dc_num].spot_demand[i]) < self.qty_to_reduce[i] - self.buffer or demand_centres[dc_num].spot_demand_to_reduce_exact[i] == 0:
                                    demand_centres[dc_num].spot_profit_loss_placeholder[i] = 1e5
                                else:
                                    pass
                            
                            self.min_list.append(demand_centres[dc_num].spot_profit_loss_placeholder[i])
                    
                    if any(self.min_list):
                        print(self.min_list)
                        
                    self.min_value[i] = int(min(self.min_list))
                    
                    # Getting minimum profit Demand centre (DC1, DC2, or DC3)
                    self.min_index[i] = min(range(len(self.min_list)),key=self.min_list.__getitem__)
                    
                    #%%
                    if self.min_value[i] > 0:
                        
                        # Demand Centre 1
                        # if self.min_index[i] == 0:
                        print(f"For best profit, it is recommended to reduce Spot Order for Demand Centre {self.min_index[i] +1} \
in {demand_centres[self.min_index[i]].table.index[i + demand_centres[self.min_index[i]].supplier_leadtime]} by {demand_centres[self.min_index[i]].spot_demand_to_reduce_lotsize[i]} MT \
(by lot size or maximum respective spot demand) or by {demand_centres[self.min_index[i]].spot_demand_to_reduce_exact[i]} MT (by exact value).")
    
                        # Update Spot Forecast Demand
                        
                        demand_centres[self.min_index[i]].spot_forecast_demand[i + int(demand_centres[self.min_index[i]].supplier_leadtime)] = \
                            demand_centres[self.min_index[i]].spot_forecast_demand[i + int(demand_centres[self.min_index[i]].supplier_leadtime)] - \
                                demand_centres[self.min_index[i]].spot_demand_to_reduce_exact[i]
                        
                        for temp_ind in range(i + int(demand_centres[self.min_index[i]].supplier_leadtime), len(demand_centres[self.min_index[i]].table)):
                        # print(temp_ind)
                        
                            demand_centres[self.min_index[i]].total_demand[temp_ind] = demand_centres[self.min_index[i]].spot_forecast_demand[temp_ind] +\
                                demand_centres[self.min_index[i]].table['Spot Order (MT)'][temp_ind] +\
                                demand_centres[self.min_index[i]].table['Term Forecast Demand (MT)'][temp_ind] +\
                                demand_centres[self.min_index[i]].table['Term Order (MT)'][temp_ind]
    
                            # Net Requirements
                            if demand_centres[self.min_index[i]].proj_end_inv[temp_ind-1] + demand_centres[self.min_index[i]].table['Scheduled Receipts (MT)'][temp_ind] - demand_centres[self.min_index[i]].total_demand[temp_ind] <= dc_params[self.min_index[i]].safety_stock:
                                demand_centres[self.min_index[i]].net_requirements[temp_ind] = demand_centres[self.min_index[i]].total_demand[temp_ind] - demand_centres[self.min_index[i]].proj_end_inv[temp_ind-1] - demand_centres[self.min_index[i]].table['Scheduled Receipts (MT)'][temp_ind] + dc_params[self.min_index[i]].safety_stock
                            else:
                                demand_centres[self.min_index[i]].net_requirements[temp_ind] = 0
                                                       
                            # Planned Receipts
                            if i >= demand_centres[self.min_index[i]].supplier_leadtime:
                                demand_centres[self.min_index[i]].planned_receipts[temp_ind] = math.ceil(demand_centres[self.min_index[i]].net_requirements[temp_ind]/dc_params[self.min_index[i]].lotsize)*dc_params[self.min_index[i]].lotsize
                            
                            # Projected Ending Inventory
                            demand_centres[self.min_index[i]].proj_end_inv[temp_ind] = demand_centres[self.min_index[i]].proj_end_inv[temp_ind-1] + demand_centres[self.min_index[i]].table['Scheduled Receipts (MT)'][temp_ind] + demand_centres[self.min_index[i]].planned_receipts[temp_ind] - demand_centres[self.min_index[i]].total_demand[temp_ind]
    
                            # Planned Orders
                            demand_centres[self.min_index[i]].planned_orders[temp_ind - int(demand_centres[self.min_index[i]].supplier_leadtime)] = demand_centres[self.min_index[i]].planned_receipts[temp_ind]
                        
                        if i > 0:
                                            
                            for dc_count in range (0,len(demand_centres)):
                                # print(demand_centres[dc_count].supplier_selection)
                                
                                if demand_centres[dc_count].supplier_selection == self.supp_num:
                                    # print(supplier_params.supplier_availability)
                                    
                                    if supplier_params.supplier_availability == 'Yes':
                                        # self.respective_dc_demands.append(demand_centres[dc_count].planned_orders)
                                        self.respective_dc_demands[dc_count] = demand_centres[dc_count].planned_orders
                                
                                    else:
                                        self.respective_dc_demands[dc_count] = pd.Series(data=[0]*len(demand_centres[0].planned_orders), index = demand_centres[0].planned_orders.index)
                                
                                else:
                                    self.respective_dc_demands[dc_count] = pd.Series(data=[0]*len(demand_centres[0].planned_orders), index = demand_centres[0].planned_orders.index)
                            
                            self.forecast_demand = sum(self.respective_dc_demands)
                            
                            # Supplier Net Requirements
                            
                            if self.proj_end_inv[i-1] - self.forecast_demand[i] <= supplier_params.safety_stock:
                                self.net_requirements[i] = self.forecast_demand[i] - self.proj_end_inv[i-1] + supplier_params.safety_stock
                                
                            else:
                                self.net_requirements[i] = 0
                            
                            # Supplier Master Production Schedule
                            if i >= supplier_params.production_leadtime:
                                self.master_production_schedule[i] = math.ceil(self.net_requirements[i]/supplier_params.lotsize)*supplier_params.lotsize
                                # self.updated_MPS[i] = self.master_production_schedule[i]
                            
                            # Projected Ending Inventory
                            self.proj_end_inv[i] = self.proj_end_inv[i-1] + self.master_production_schedule[i] - self.forecast_demand[i]
                            
                            
                            if i < len(self.forecast_demand)-int(supplier_params.production_leadtime):
                                                        
                                # Supplier Amount to Reduce
                                if self.net_requirements[i] - supplier_params.max_weekly_production >=0:
                                    
                                    # Spot Quantity to Reduce
                                    self.qty_to_reduce[i] = self.net_requirements[i] - supplier_params.max_weekly_production
                                    
                                    # Amount to Move
                                    self.qty_to_move[i] = self.master_production_schedule[i] - supplier_params.max_weekly_production
                                else:
                                    self.qty_to_reduce[i] = 0
                                    self.qty_to_move[i] = 0
                            
                            
                            
                            
                            
                    if i >= int(supplier_params.production_leadtime):
                
                        # Planned Orders - can only be calculated backwards after leadtime has passed
                        self.planned_orders[i - int(supplier_params.production_leadtime)] = self.master_production_schedule[i]
                
                
                elif supplier_params.method == 'Prebuild Inventory':
                    
                    self.master_production_schedule[i] = self.master_production_schedule[i] - self.qty_to_move[i]
                    ind_move = 1
                    
                    while self.qty_to_move[i] != 0:
                        
                        if i-ind_move >=0:
                            
                            if self.master_production_schedule[i-ind_move] < supplier_params.max_weekly_production:
                                print(f"Moving production quantity with amount of {supplier_params.lotsize} from {self.master_production_schedule.index[i]} to {self.master_production_schedule.index[i-ind_move]}.")
                                self.master_production_schedule[i-ind_move] = self.master_production_schedule[i-ind_move] + supplier_params.lotsize
                                self.qty_to_move[i] = self.qty_to_move[i] - supplier_params.lotsize
        
                            else:
                                ind_move +=1
                                
                        else:
                            
                            print(f"\nProduction schedule is maxed out. \
    Couldn't move production quantity in {self.master_production_schedule.index[i]}. \
    Please reduce order.\nOPTIMISATION PROCESS ABORTED.")
                            self.status = "Production maxed out"
                            break
                    
                    else:
                        print(f"Production schedule is okay in {self.master_production_schedule.index[i]}")
                    
                
            if supplier_params.method == 'Prebuild Inventory' and self.status == "Production okay":
                
                for i in range(int(supplier_params.production_leadtime),len(self.forecast_demand)):
                    
                    # Planned Orders - can only be calculated backwards after leadtime has passed
                    self.planned_orders[i - int(supplier_params.production_leadtime)] = self.master_production_schedule[i]
                
                print ('Prebuilt Inventory done successfully without violation.')
                
            else:
                pass
            
def print_out(dc):
    
    out=pd.DataFrame({
        
        'Spot Forecast Demand(MT)': dc.table['Spot Forecast Demand(MT)'],
        'Spot Order (MT)': dc.table['Spot Order (MT)'],
        'Term Forecast Demand (MT)': dc.table['Term Forecast Demand (MT)'],
        'Term Order (MT)': dc.table['Term Order (MT)'],
        'Total DC demand': dc.total_demand,
        'Scheduled Receipts': dc.table['Scheduled Receipts (MT)'],
        'Proj End Inv': dc.proj_end_inv,
        'Net Req': dc.net_requirements,
        'Planned Receipts': dc.planned_receipts,
        'Planned Orders': dc.planned_orders,
        'Truck Count 10T': dc.truck_count_10T,
        'Truck Count 20T': dc.truck_count_20T,
        'Total_shipment_cost': dc.total_shipment_cost,        
        'Product Unit Cost (RM/MT)': dc.table['Product Unit Cost (RM/MT)'],
        'Product Cost': dc.product_cost,
        'Total Supply Cost': dc.totalsupply_cost,        
        'Product Selling Price (RM/MT)': dc.table['Product Selling Price (RM/MT)'],
        'Revenue (RM)': dc.revenue,
        'Profit (RM)': dc.profit,
        
        'Spot Demand': dc.spot_demand,
        'SDTR lotsize': dc.spot_demand_to_reduce_lotsize, 
        'SDTR exact': dc.spot_demand_to_reduce_exact,
        '(Spot) Truck 10T': dc.spot_truck_count_10T,
        '(Spot) Truck 20T': dc.spot_truck_count_20T,
        '(Spot) Shipment Cost': dc.spot_shipment_cost,
        '(Spot) Product Cost': dc.spot_product_cost,
        '(Spot) Total Supply Cost': dc.spot_total_supply_cost,
        '(Spot) Drop Revenue': dc.spot_drop_in_revenue,
        '(Spot) Profit Loss': dc.spot_profit_loss,
        '(Spot) Final Profit': dc.final_profit,
        
        })
    
    return out