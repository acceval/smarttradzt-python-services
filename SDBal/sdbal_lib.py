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
    
    def __init__(self, excelfile, sheet_name, threemonths_demand_forecast, prod_qty_m, initial_end_inv, final_month_end_total_order):
        self.n = 3
        self.excelfile = excelfile
        self.sheet_name = sheet_name
        
        # Supplier parameters
        self.table = pd.read_excel(self.excelfile, sheet_name=self.sheet_name, skiprows = 6, nrows = 5, usecols = 'C:D')
        self.table.index = self.table['Params']
        self.table.drop('Params', axis=1, inplace=True)
        
        # self.initial_end_inv = self.table.loc['Initial Inventory','Value']
        self.initial_end_inv = initial_end_inv
        self.safety_stock = self.table.loc['Safety Stock','Value']
        self.final_month_end_total_order = final_month_end_total_order
        self.demand_forecast_month_m_minus_1 = threemonths_demand_forecast
                
        # Initialisation
        # self.starting_inventory = [0]*self.n
        self.prod_plan = [0]*self.n
        self.planned_starting_inventory = [0]*self.n
        self.planned_ending_inventory = [0]*self.n
        self.planned_available_inventory = [0]*self.n
        self.planned_available_supply_qty = [0]*self.n
        self.planned_supply_demand_balance = [0]*self.n
        # self.updated_prod_plan = [0]*self.n
        
        self.prod_plan[0] = prod_qty_m
        self.planned_starting_inventory[0] = self.initial_end_inv + self.prod_plan[0]
        self.planned_available_inventory[0] = self.initial_end_inv - self.safety_stock
        self.planned_ending_inventory[0] = self.planned_starting_inventory[0] - self.demand_forecast_month_m_minus_1[0]
        self.planned_available_supply_qty[0] = self.planned_available_inventory[0] + self.prod_plan[0]
        self.planned_supply_demand_balance[0] = self.planned_available_supply_qty[0] - self.demand_forecast_month_m_minus_1[0]
        # self.initial_end_inv_month_m = self.planned_ending_inventory[0]
        
        # Updates months m-1
        for i in range(1,self.n):
            # print(i)           
            self.planned_available_inventory[i] = self.planned_ending_inventory[i-1] - self.safety_stock
            self.prod_plan[i] = self.demand_forecast_month_m_minus_1[i] - self.planned_available_inventory[i]
            self.planned_starting_inventory[i] = self.planned_ending_inventory[i-1] + self.prod_plan[i]
            self.planned_ending_inventory[i] = self.planned_starting_inventory[i] - self.demand_forecast_month_m_minus_1[i]      
            self.planned_available_supply_qty[i] = self.planned_available_inventory[i] + self.prod_plan[i]
            self.planned_supply_demand_balance[i] = self.planned_available_supply_qty[i] - self.demand_forecast_month_m_minus_1[i]
            # self.updated_prod_plan[i-1] = self.prod_plan[i]
        
        # Outputs
        self.initial_end_inv_next_month = self.planned_starting_inventory[0] - self.final_month_end_total_order
        self.supply_plan_m = self.prod_plan[1]
        