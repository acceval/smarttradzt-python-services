# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 08:20:05 2020

@author: James Ang
"""

import json
import math
import copy
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Allocations:
    
    def __init__(self, data):
        
        self.data = data
        self.date_str = self.data.get("datetime_receive_goods_after_quarantine")  
        self.format_date = "%d-%m-%Y %H:%M"
        self.datetime_receive_allocation = datetime.strptime(self.date_str, self.format_date)
        
        self.numdays = 5
        self.date_truncated = datetime.date(self.datetime_receive_allocation)
        self.date_range = [self.date_truncated + timedelta(days=x) for x in range(self.numdays)] # Input as date range?
        self.allocation = self.data.get("allocation")

class Trucks:
    
    def __init__(self, data):
        
        self.data = data
        self.name = self.data.get('name')
        self.current_location =self.data.get('current_location')
        self.current_location_zipcode = self.data.get('current_location_zipcode')
        self.min_lotsize = self.data.get('min_lotsize')
        self.max_lotsize = self.data.get('max_lotsize')
        self.truck_type = self.data.get('truck_type')
        self.max_daily_delivery_hours = self.data.get('max_daily_delivery_hours')
        # df.to_dict('series')
        
class Warehouses:
    
    def __init__(self, data, allocation):
        
        self.data = data
        self.name = self.data.get('name')
        self.zipcode = self.data.get('zipcode')
        self.warehouses_supplyto =  self.data.get('supply_to')
        
        self.hosp_allocation = allocation[0].allocation         #object
        # self.hosp_alloc = self.hosp_allocation.allocation
        
        self.warehouse_breakdown = []
        
        for item in self.hosp_allocation :
            if item.get("name") in self.warehouses_supplyto:
                # print(item.get("name"))
                self.warehouse_breakdown.append(item)
                
        self.warehouse_quantity = sum([data.get("quantity") for data in self.warehouse_breakdown])
        self.warehouse_allocation = [{'name':self.name,'quantity': self.warehouse_quantity, 'zipcode': self.zipcode}]
        
class Suppliers:
    
    def __init__(self, data, allocation, warehouse):
        
        self.data = data
        self.name = self.data.get('name')
        self.zipcode = self.data.get('zipcode')
        self.suppliers_supplyto =  self.data.get('supply_to')
        
        self.warehouse_allocation = [wh.warehouse_allocation[0] for wh in warehouse]
        self.hosp_allocation = allocation[0].allocation
        # self.hosp_alloc = self.hosp_allocation.allocation
        
        self.all_allocation = self.hosp_allocation + self.warehouse_allocation
        
        self.supplier_breakdown = []
        self.supplier_breakdown_hosp_only = []
        
        for item in self.all_allocation :
            if item.get("name") in self.suppliers_supplyto:
                # print(item.get("name"))
                self.supplier_breakdown.append(item)
                
        # for item in self.hosp_allocation :
        #     if item.get("name") in self.suppliers_supplyto:
        #         # print(item.get("name"))
        #         self.supplier_breakdown_hosp_only.append(item)
                
        # self.supplier_total_alloc_quantity = sum([data.get("quantity") for data in self.supplier_breakdown])
        # self.supplier_allocation = [{'name':self.name,'quantity': self.supplier_total_alloc_quantity, 'zipcode': self.zipcode}]
        # self.supplier_breakdown_df = pd.DataFrame(self.supplier_breakdown)
        
        # self.supplier_total_alloc_quantity_hosp_only = sum([data.get("quantity") for data in self.supplier_breakdown_hosp_only])
        # self.supplier_breakdown_hosp_only_df = pd.DataFrame(self.supplier_breakdown_hosp_only)
        # self.supplier_breakdown_hosp_only_df['percent'] = self.supplier_breakdown_hosp_only_df.loc[:,'quantity']*100/self.supplier_total_alloc_quantity_hosp_only
        
class Routes:
    
    def __init__(self, route, entity, supplier, trucks):
        
        # Route
        self.data_route = route
        self.route_name = self.data_route.get('name')
        self.route_truck_name = self.data_route.get('truck')
        
        self.route_origin = self.data_route.get('origin')
        self.route_dest = [item.get('name') for item in self.data_route.get('destinations')]
        self.route_qty = [item.get('quantity') for item in self.data_route.get('destinations')]
        self.route_final = self.data_route.get('final_destination')
        
        # Supplier - for 1 supplier
        self.supplier_objs = supplier
        self.supplier_names = [item.name for item in self.supplier_objs]
        self.supplier_index = self.supplier_names.index(self.route_origin)
        self.supplier_breakdown_all = [item.supplier_breakdown for item in self.supplier_objs][self.supplier_index]
        self.supplier_breakdown_all_names = [item.get('name') for item in self.supplier_breakdown_all]
        
        self.breakdown_route_only = []
        for item in self.supplier_breakdown_all:
            if item.get("name") in self.route_dest:
                # print(item.get("name"))
                self.breakdown_route_only.append(item)
        
        self.route_total_alloc_quantity = sum([data.get("quantity") for data in self.breakdown_route_only])
        self.breakdown_route_only_df = pd.DataFrame(self.breakdown_route_only)
        self.hosp_percent = self.breakdown_route_only_df.loc[:,'quantity']*100/self.route_total_alloc_quantity
        
        
        # self.supplier_breakdown_hosp_only_df = [item.supplier_breakdown_hosp_only_df for item in self.supplier_objs][self.supplier_index]
        # self.route_total_alloc_quantity = [item.supplier_total_alloc_quantity_hosp_only for item in self.supplier_objs][self.supplier_index]
        # self.hosp_percent = self.supplier_breakdown_hosp_only_df['percent']
        self.hosp_percent_col = [[item/100] for item in self.hosp_percent]
        self.breakdown_route_hosp_names = self.breakdown_route_only_df['name'].to_list()
        
        
        # Trucks
        self.trucks_obj = trucks
        self.truck_names = [item.name for item in self.trucks_obj]
        self.truck_index = self.truck_names.index(self.route_truck_name)
        self.truck_current_location = [item.current_location for item in self.trucks_obj][self.truck_index]
        self.truck_current_location_zipcode = [item.current_location_zipcode for item in self.trucks_obj][self.truck_index]
        self.truck_min_lotsize = [item.min_lotsize for item in self.trucks_obj][self.truck_index]
        self.truck_max_lotsize = [item.max_lotsize for item in self.trucks_obj][self.truck_index]
        self.truck_max_daily_delivery_hours = [item.max_daily_delivery_hours for item in self.trucks_obj][self.truck_index]
        
                
        # Start datetime
        self.format_date = "%d-%m-%Y %H:%M"
        self.start_del_datetime_str = self.data_route.get('datetime_start_delivery')
        self.start_del_datetime = datetime.strptime(self.start_del_datetime_str, self.format_date)
        # self.start_del_date = datetime.date(self.start_del_datetime)
        
        # End datetime
        self.end_del_datetime_str = self.data_route.get('datetime_end_delivery')
        self.end_del_datetime = datetime.strptime(self.end_del_datetime_str, self.format_date)
        # self.end_del_date = datetime.date(self.end_del_datetime)
        
        # Date Range
        self.date_range = list(pd.date_range(self.start_del_datetime,self.end_del_datetime,freq='d').to_pydatetime())
        
        # Truck Daily delivery
        self.truck_daily_delivery = []
        remaining = self.route_total_alloc_quantity
        for i in range(0,len(self.date_range)):
            print(i)
            if remaining > self.truck_max_lotsize:
                
                self.truck_daily_delivery.append(self.truck_max_lotsize)
                remaining = remaining - self.truck_max_lotsize
            else:
                self.truck_daily_delivery.append(remaining)
                remaining = remaining - remaining
        
        self.truck_daily_delivery_percent = [item/self.route_total_alloc_quantity for item in self.truck_daily_delivery]
        self.delivery_calcd = np.round(np.dot(self.hosp_percent_col,[self.truck_daily_delivery_percent])*self.route_total_alloc_quantity)

        self.delivery_calcd_df=pd.DataFrame(self.delivery_calcd, columns=self.date_range, index = self.breakdown_route_hosp_names)
        
        # Extracting all entities objects and properties
        self.entity_objs = entity
        self.entity_obj_names = [item.origin for item in self.entity_objs]
        self.entity_obj_unloading_times = [item.unloading_time for item in self.entity_objs]
        
        # Only Origin object and property
        self.origin_index =  self.entity_obj_names.index(self.route_origin)
        self.origin_entity_obj = self.entity_objs[self.origin_index]
        
        # Initialise start time, location, duration
        self.start_time = self.date_range[0]
        self.planned_time = [self.start_time]           # First entry - Start Time
        self.planned_location = [self.route_origin]
        self.planned_duration = ['-']
        self.description = ['Start Time']
        
        # Loading at origin
        self.entity_origin_loadingtime = self.origin_entity_obj.loading_time
        self.planned_time.append(self.start_time + timedelta(hours=self.entity_origin_loadingtime))  # Second entry - Loading time
        self.planned_location.append(self.route_origin)
        self.planned_duration.append(f'{self.entity_origin_loadingtime} hr')
        self.description.append(f'Loading Time at {self.route_origin}')
                
        self.entity_ori_dest_names = self.origin_entity_obj.destination_names
        self.entity_ori_dest_leadtimes = self.origin_entity_obj.destination_leadtimes
        
                
        # First Destination from origin
        self.first_dest_index = self.entity_ori_dest_names.index(self.route_dest[0])
        self.first_dest_leadtime = self.entity_ori_dest_leadtimes[self.first_dest_index]
        print(f" From Origin: {self.route_origin} to First Destination: {self.route_dest[0]}")
        print(f" Route Destinations : {', '.join(self.route_dest)}")
                
        # self.entity_origins = [item.origin for item in self.origin_entity_obj]
        # self.entity_origin_loadingtimes = [item.loading_time for item in self.origin_entity_obj]
        # self.entity_ori_dest_names = [item.destination_names for item in self.origin_entity_obj]
        # self.entity_ori_dest_leadtimes = [item.destination_leadtimes for item in self.origin_entity_obj]
        if not self.route_final:
            self.route_names_all = [self.route_origin] + self.route_dest
            print(f" Final Destinations : {self.route_dest[-1]}\n")
        else:
            self.route_names_all = [self.route_origin] + self.route_dest + [self.route_final]
            print(f" Final Destinations : {self.route_final}\n")
        
        # Route destination info
        # self.dest_lead_times = []
        # self.dest_unload_times_route = []
        
        # Calculate route time and display time
        if len(self.route_names_all)>=2:
            for i in range(0,len(self.route_names_all)-1):
                print(f"Destinations: {self.route_names_all[i+1]}")
                
                # Calculate lead times
                self.route_ori_index = self.entity_obj_names.index(self.route_names_all[i])
                self.route_ori_obj = self.entity_objs[self.route_ori_index]
                self.route_dest_names = self.route_ori_obj.destination_names
                self.route_dest_leadtimes = self.route_ori_obj.destination_leadtimes
                self.route_dest_index = self.route_ori_obj.destination_names.index(self.route_names_all[i+1])
                self.route_dest_leadtime = self.route_ori_obj.destination_leadtimes[self.route_dest_index]
                # self.dest_lead_times.append(self.route_dest_leadtime)
                
                self.planned_time.append(self.planned_time[-1] + timedelta(hours=self.route_dest_leadtime))  # Third entry - Travelling time
                self.planned_location.append(self.route_names_all[i+1])
                self.planned_duration.append(f'{self.route_dest_leadtime} hr')
                self.description.append(f'Travelling Time from {self.route_names_all[i]} to {self.route_names_all[i+1]}')
                
                
                # Calculate unload times
                self.dest_index =  self.entity_obj_names.index(self.route_names_all[i+1])
                self.dest_unload_time = self.entity_obj_unloading_times[self.dest_index]
                # self.dest_unload_times_route.append(self.entity_obj_unloading_times[self.dest_index])
                if self.dest_unload_time > 0:
                    self.planned_time.append(self.planned_time[-1] + timedelta(hours=self.dest_unload_time))  # Fourth entry - Unloading time
                    self.planned_location.append(self.route_names_all[i+1])
                    self.planned_duration.append(f'{self.dest_unload_time} hr')
                    self.description.append(f'Goods unloading time at {self.route_names_all[i+1]}')
                
        else:
            pass
        
        # # Last Destination - back to origin
        # self.last_dest_index = self.entity_ori_dest_names.index(self.route_dest[-1])
        # self.last_dest_leadtime = self.origin_entity_obj.destination_leadtimes[0]
        
        # Total time
        self.planned_completion_time = [item.strftime("%d-%m-%Y %H:%M") for item in self.planned_time]
        self.total_time = self.entity_origin_loadingtime + self.first_dest_leadtime

        
class Entities:
    
    def __init__(self, data):
        
        self.data = data
        self.origin = self.data.get('origin')
        self.loading_time = self.data.get('loading_time')
        self.unloading_time = self.data.get('unloading_time')
        self.destination_info = self.data.get('to_destination_info')
        self.destination_names = [item.get('destination') for item in self.destination_info]
        self.destination_leadtimes = [item.get('leadtime') for item in self.destination_info]
        self.destination_distance = [item.get('distance') for item in self.destination_info]
        # self.entities = self.data.get('entity_property')
        # self.name = self.data.get('name')