# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 12:20:46 2020

@author: James Ang
"""
import pandas as pd

class Month_Demand:
    
    def __init__(self, excelfile, sheet_name):
        self.excelfile = excelfile
        self.sheet_name = sheet_name
        self.table = pd.read_excel(self.excelfile, sheet_name=self.sheet_name, skiprows = 5, nrows = 4, usecols = 'N:O')
        self.table.index = self.table['Country']
        self.table.drop('Country', axis=1, inplace=True)
        self.totaldemand = sum(self.table['Forecast'])
        
class Month_Order:
    
    def __init__(self, excelfile, sheet_name):
        self.excelfile = excelfile
        self.sheet_name = sheet_name
        self.table = pd.read_excel(self.excelfile, sheet_name=self.sheet_name, skiprows = 5, nrows = 4, usecols = 'N,P')
        self.table.index = self.table['Country']
        self.table.drop('Country', axis=1, inplace=True)

class Supp_Params:
    
    def __init__(self, excelfile, sheet_name):
        self.excelfile = excelfile
        self.sheet_name = sheet_name
        self.table = pd.read_excel(self.excelfile, sheet_name=self.sheet_name, skiprows = 6, nrows = 4, usecols = 'C:D')
        self.table.index = self.table['Params']
        self.table.drop('Params', axis=1, inplace=True)

class Gen_Supp_Plan:
    
    def __init__(self, excelfile, sheet_name, threemonths_demand_forecast, prod_qty_m, initial_end_inv, final_month_end_total_order, max_prod_limit, target_ending_inventory):
        self.n = 3
        self.excelfile = excelfile
        self.sheet_name = sheet_name
        self.max_prod_limit = max_prod_limit
        self.target_ending_inventory = target_ending_inventory
        
        # Supplier parameters
        self.table = pd.read_excel(self.excelfile, sheet_name=self.sheet_name, skiprows = 6, nrows = 5, usecols = 'C:D')
        self.table.index = self.table['Params']
        self.table.drop('Params', axis = 1, inplace = True)
        
        self.initial_end_inv = initial_end_inv
        self.safety_stock = self.table.loc['Safety Stock','Value']
        self.final_month_end_total_order = final_month_end_total_order
        self.demand_forecast_month_m_minus_1 = threemonths_demand_forecast
                
        # Initialisation
        self.prod_plan = [0]*self.n
        self.starting_inventory = [0]*self.n
        self.ending_inventory = [0]*self.n
        self.available_inventory = [0]*self.n
        self.available_supply_qty = [0]*self.n
        self.supply_demand_balance = [0]*self.n
        self.spot_allocation_to_reduce = [0]*self.n
        
        self.prod_plan[0] = prod_qty_m
        self.starting_inventory[0] = self.initial_end_inv + self.prod_plan[0]
        self.available_inventory[0] = self.initial_end_inv - self.target_ending_inventory[0]
        self.ending_inventory[0] = self.starting_inventory[0] - self.demand_forecast_month_m_minus_1[0]
        self.available_supply_qty[0] = self.available_inventory[0] + self.prod_plan[0]
        self.supply_demand_balance[0] = self.available_supply_qty[0] - self.demand_forecast_month_m_minus_1[0]
        # self.initial_end_inv_month_m = self.ending_inventory[0]
        
        # Updates months m-1
        for i in range(1,self.n):
            # print(i)           
            self.available_inventory[i] = self.ending_inventory[i-1] - self.target_ending_inventory[i]
            self.prod_plan[i] = self.demand_forecast_month_m_minus_1[i] - self.available_inventory[i]
            
            if self.prod_plan[i] > self.max_prod_limit:
                self.spot_allocation_to_reduce[i] = self.prod_plan[i] - self.max_prod_limit
                self.prod_plan[i] = self.max_prod_limit
                print(f"Production Quantity in Month {i+1} is above production limit. Reduce production quantity by {self.spot_allocation_to_reduce[i]} MT.")
            else:
                pass
            
            self.starting_inventory[i] = self.ending_inventory[i-1] + self.prod_plan[i]
            self.ending_inventory[i] = self.starting_inventory[i] - self.demand_forecast_month_m_minus_1[i]      
            self.available_supply_qty[i] = self.available_inventory[i] + self.prod_plan[i]
            self.supply_demand_balance[i] = self.available_supply_qty[i] - self.demand_forecast_month_m_minus_1[i]
            # self.updated_prod_plan[i-1] = self.prod_plan[i]
        
        # Outputs
        self.initial_end_inv_next_month = self.starting_inventory[0] - self.final_month_end_total_order
        if self.initial_end_inv_next_month < self.safety_stock:
            print(f'Execution Month Ending Inventory is below Safety Stock level ({self.safety_stock} MT) at {self.initial_end_inv_next_month} MT.')
        
        self.supply_plan_next_month = self.prod_plan[1]