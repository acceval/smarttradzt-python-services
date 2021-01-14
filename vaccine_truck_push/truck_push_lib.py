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
        self.datetime_receive_allocation = allocation[0].datetime_receive_allocation
        
        self.all_allocation = self.hosp_allocation + self.warehouse_allocation
        
        self.supplier_breakdown = []
        
        for item in self.all_allocation :
            if item.get("name") in self.suppliers_supplyto:
                # print(item.get("name"))
                self.supplier_breakdown.append(item)


def intersperse(lst, item):
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result

class Routes:
    
    def __init__(self, route, entity, supplier, trucks):
        
        # Route
        self.data_route = route
        self.route_name = self.data_route.get('name')
        self.route_truck_name = self.data_route.get('truck')
        
        self.route_origin = self.data_route.get('origin')
        self.route_dest = [item.get('name') for item in self.data_route.get('destinations')]
        # self.route_qty = [item.get('quantity') for item in self.data_route.get('destinations')]
        self.route_final = self.data_route.get('final_destination')
        self.route_type = self.data_route.get('route_type')
        
        # Supplier - for 1 supplier
        self.supplier_objs = supplier
        self.supplier_names = [item.name for item in self.supplier_objs]
        self.supplier_index = self.supplier_names.index(self.route_origin)
        self.supplier_breakdown_all = [item.supplier_breakdown for item in self.supplier_objs][self.supplier_index]
        self.supplier_breakdown_all_names = [item.get('name') for item in self.supplier_breakdown_all]
        self.datetime_receive_allocation = supplier[0].datetime_receive_allocation
        # self.date_sunday = self.datetime_receive_allocation + timedelta( (6-self.datetime_receive_allocation.weekday()) % 7 )
        
        # Trucks
        self.trucks_obj = trucks
        self.truck_names = [item.name for item in self.trucks_obj]
        self.truck_index = self.truck_names.index(self.route_truck_name)
        self.truck_current_location = [item.current_location for item in self.trucks_obj][self.truck_index]
        # self.truck_current_location_zipcode = [item.current_location_zipcode for item in self.trucks_obj][self.truck_index]
        self.truck_min_lotsize = [item.min_lotsize for item in self.trucks_obj][self.truck_index]
        self.truck_max_lotsize = [item.max_lotsize for item in self.trucks_obj][self.truck_index]
        self.truck_max_daily_delivery_hours = [item.max_daily_delivery_hours for item in self.trucks_obj][self.truck_index]
        
        # Route breakdown
        self.breakdown_route_only_weekly = []
        for item in self.supplier_breakdown_all:    # There can be more hospitals, used that specified in route only
            if item.get("name") in self.route_dest:
                # print(item.get("name"))
                self.breakdown_route_only_weekly.append(item)
        
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
        
        # Calculation for maxed
        maxed_array = np.zeros( (len(self.breakdown_route_only_weekly), len(self.date_range)) )
        
        for i in range(0,len(self.breakdown_route_only_weekly)):
            remaining = self.breakdown_route_only_weekly[i].get("quantity")
            print(remaining)
            
            for j in range(0,len(self.date_range)):
                print(j)
                if remaining > self.truck_max_lotsize:
                    
                    maxed_array[i,j] = self.truck_max_lotsize
                    remaining = remaining - self.truck_max_lotsize
                else:
                    maxed_array[i,j] = remaining
                    remaining = remaining - remaining
            
        
        self.route_alloc_quantity = [data.get("quantity") if data.get("quantity")<=self.truck_max_lotsize else self.truck_max_lotsize for data in self.breakdown_route_only_weekly ]
        
        # Calculation for shared
        self.route_total_alloc_quantity = sum([data.get("quantity") for data in self.breakdown_route_only_weekly])
        self.breakdown_route_only_weekly_df = pd.DataFrame(self.breakdown_route_only_weekly)
        self.hosp_percent = self.breakdown_route_only_weekly_df.loc[:,'quantity']*100/self.route_total_alloc_quantity
        self.hosp_percent_col = [[item/100] for item in self.hosp_percent]
        self.breakdown_route_hosp_names = self.breakdown_route_only_weekly_df['name'].to_list()
        
        
        # Truck Daily delivery
        self.truck_daily_delivery = []
        remaining = self.route_total_alloc_quantity
        
        for i in range(0,len(self.date_range)):
            # print(i)
            if remaining > self.truck_max_lotsize:
                
                self.truck_daily_delivery.append(self.truck_max_lotsize)
                remaining = remaining - self.truck_max_lotsize
            else:
                self.truck_daily_delivery.append(remaining)
                remaining = remaining - remaining
        
        self.truck_daily_delivery_percent = [item/self.route_total_alloc_quantity for item in self.truck_daily_delivery]
        # delivery_calcd = np.round(np.dot(self.hosp_percent_col,[self.truck_daily_delivery_percent])*self.route_total_alloc_quantity)
        
        
        if self.route_type == "shared":
            delivery_calcd = np.round(np.dot(self.hosp_percent_col,[self.truck_daily_delivery_percent])*self.route_total_alloc_quantity)
            self.route_daily_alloc=pd.DataFrame(delivery_calcd, columns=self.date_range, index = self.breakdown_route_hosp_names)
        elif self.route_type == "maxed":
            self.route_daily_alloc=pd.DataFrame(maxed_array, columns=self.date_range, index = self.breakdown_route_hosp_names)
        else:
            pass
        
        # Extracting all entities objects and properties
        self.entity_objs = entity
        self.entity_obj_names = [item.origin for item in self.entity_objs]
        self.entity_obj_unloading_times = [item.unloading_time for item in self.entity_objs]
        
        # Only Origin object and property
        self.origin_index =  self.entity_obj_names.index(self.route_origin)
        self.origin_entity_obj = self.entity_objs[self.origin_index]
        self.entity_ori_dest_names = self.origin_entity_obj.destination_names
        self.entity_ori_dest_leadtimes = self.origin_entity_obj.destination_leadtimes
        
        self.schedules = []
        
        if self.route_type == "shared" or self.route_type == "maxed":
        # Iterating Daily
            for dt in self.date_range:
                # print(dt)
                route_daily_alloc = self.route_daily_alloc.loc[:,dt]
                self.route_dest_daily = route_daily_alloc[route_daily_alloc>0].index.to_list()
    
                
                if not self.route_dest_daily:
    
                    pass
                
                else:
                    
                
                    # Initialise start time, location, duration
                    self.start_time = dt
                    # self.start_time = self.date_range[0]
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
                            
                    
                    # First Destination from origin
                    
                    # self.first_dest_index = self.entity_ori_dest_names.index(self.route_dest_daily[0])
                    # self.first_dest_leadtime = self.entity_ori_dest_leadtimes[self.first_dest_index]
                    print(f" Origin: {self.route_origin} to First Destination: {self.route_dest_daily[0]}")
                    print(f" Routing Destinations : {', '.join(self.route_dest_daily)}")
                        
                    
                    # Getting routes into 
                    if not self.route_final:
                        self.route_names_all = [self.route_origin] + self.route_dest_daily
                        print(f" Final Destination : {self.route_dest_daily[-1]}\n")
                    else:
                        if self.route_type == "maxed":
                            self.route_dest_daily=intersperse(self.route_dest_daily, self.route_origin)
                        else:
                            pass
                        self.route_names_all = [self.route_origin] + self.route_dest_daily + [self.route_final]
                        print(f" Final Destination : {self.route_final}\n")
                
                
                    # Route destination info            
                    # Calculate route time and display time
                    if len(self.route_names_all)>=2:
                        for i in range(0,len(self.route_names_all)-1):
                            # print(f"Delivering to Destination: {self.route_names_all[i+1]}")
                            
                            # Calculate lead times
                            self.route_ori_index = self.entity_obj_names.index(self.route_names_all[i])     # getting index from entity list
                            self.route_ori_obj = self.entity_objs[self.route_ori_index]
                            self.route_dest_names = self.route_ori_obj.destination_names
                            self.route_dest_leadtimes = self.route_ori_obj.destination_leadtimes
                            self.route_dest_index = self.route_dest_names.index(self.route_names_all[i+1])
                            self.route_dest_leadtime = self.route_ori_obj.destination_leadtimes[self.route_dest_index]
                            
                            self.planned_time.append(self.planned_time[-1] + timedelta(hours=self.route_dest_leadtime))  # Third entry - Travelling time
                            self.planned_location.append(self.route_names_all[i+1])
                            self.planned_duration.append(f'{self.route_dest_leadtime} hr')
                            self.description.append(f'Travelling Time from {self.route_names_all[i]} to {self.route_names_all[i+1]}')
                            
                            
                            # Calculate unload times
                            self.dest_index =  self.entity_obj_names.index(self.route_names_all[i+1])
                            self.dest_unload_time = self.entity_obj_unloading_times[self.dest_index]
                            
                            if self.dest_unload_time > 0:
                                self.planned_time.append(self.planned_time[-1] + timedelta(hours=self.dest_unload_time))  # Fourth entry - Unloading time
                                self.planned_location.append(self.route_names_all[i+1])
                                self.planned_duration.append(f'{self.dest_unload_time} hr')
                                self.description.append(f'Goods unloading time at {self.route_names_all[i+1]}')
                                
                            elif self.dest_unload_time == 0 and i !=len(self.route_names_all)-2:
                                self.planned_time.append(self.planned_time[-1] + timedelta(hours=self.entity_origin_loadingtime))  # Fourth entry - Unloading time
                                self.planned_location.append(self.route_names_all[i+1])
                                self.planned_duration.append(f'{self.entity_origin_loadingtime} hr')
                                self.description.append(f'Goods loading time at {self.route_names_all[i+1]}')
                            else:
                                pass

                    else:
                        pass
                    
                    self.planned_time = [item.time() for item in self.planned_time]
                    self.daily_dict = {
                        "time": self.planned_time, 
                        "location": self.planned_location,
                        "duration": self.planned_duration,
                        "description": self.description
                        }
                    self.table = pd.DataFrame(self.daily_dict)
                    self.table = json.loads(self.table.to_json(orient='records'))
                    self.table_final = {"date": dt.strftime("%d-%m-%Y"), "daily_schedule": self.table}
                    self.schedules.append(self.table_final)
        
        # elif self.route_type == "maxed":
            
        #     for dt in self.date_range:
        #         # print(dt)
        #         route_daily_alloc = self.route_daily_alloc.loc[:,dt]
        #         self.route_dest_daily = route_daily_alloc[route_daily_alloc>0].index.to_list()
    
                
        #         if not self.route_dest_daily:
    
        #             pass
                
        #         else:
                    
        #             # Initialise start time, location, duration
        #             self.start_time = dt
        #             # self.start_time = self.date_range[0]
        #             self.planned_time = [self.start_time]           # First entry - Start Time
        #             self.planned_location = [self.route_origin]
        #             self.planned_duration = ['-']
        #             self.description = ['Start Time']
                
        #             # Loading at origin
        #             self.entity_origin_loadingtime = self.origin_entity_obj.loading_time
        #             self.planned_time.append(self.start_time + timedelta(hours=self.entity_origin_loadingtime))  # Second entry - Loading time
        #             self.planned_location.append(self.route_origin)
        #             self.planned_duration.append(f'{self.entity_origin_loadingtime} hr')
        #             self.description.append(f'Loading Time at {self.route_origin}')
                    
        #             # First Destination from origin
                    
        #             print(f" Origin: {self.route_origin} to First Destination: {self.route_dest_daily[0]}")
        #             print(f" Routing Destinations : {', '.join(self.route_dest_daily)}")
                    
        #             # Getting routes into 
        #             if not self.route_final:
        #                 self.route_names_all = [self.route_origin] + self.route_dest_daily
        #                 print(f" Final Destination : {self.route_dest_daily[-1]}\n")
        #             else:
        #                 self.route_dest_daily=intersperse(self.route_dest_daily, self.route_origin)
        #                 self.route_names_all = [self.route_origin] + self.route_dest_daily + [self.route_final]
        #                 print(f" Final Destination : {self.route_final}\n")
                
                
        #             # Route destination info            
        #             # Calculate route time and display time
        #             if len(self.route_names_all)>=2:
        #                 for i in range(0,len(self.route_names_all)-1):
        #                     # print(f"Delivering to Destination: {self.route_names_all[i+1]}")
        #                     # Calculate lead times
        #                     self.route_ori_index = self.entity_obj_names.index(self.route_names_all[i])     # getting index from entity list
        #                     self.route_ori_obj = self.entity_objs[self.route_ori_index]
        #                     self.route_dest_names = self.route_ori_obj.destination_names
        #                     self.route_dest_leadtimes = self.route_ori_obj.destination_leadtimes
        #                     self.route_dest_index = self.route_dest_names.index(self.route_names_all[i+1])
        #                     self.route_dest_leadtime = self.route_ori_obj.destination_leadtimes[self.route_dest_index]
                            
        #                     self.planned_time.append(self.planned_time[-1] + timedelta(hours=self.route_dest_leadtime))  # Third entry - Travelling time
        #                     self.planned_location.append(self.route_names_all[i+1])
        #                     self.planned_duration.append(f'{self.route_dest_leadtime} hr')
        #                     self.description.append(f'Travelling Time from {self.route_names_all[i]} to {self.route_names_all[i+1]}')
                            
                            
        #                     # Calculate unload times
        #                     self.dest_index =  self.entity_obj_names.index(self.route_names_all[i+1])
        #                     self.dest_unload_time = self.entity_obj_unloading_times[self.dest_index]
                            
        #                     if self.dest_unload_time > 0:
        #                         self.planned_time.append(self.planned_time[-1] + timedelta(hours=self.dest_unload_time))  # Fourth entry - Unloading time
        #                         self.planned_location.append(self.route_names_all[i+1])
        #                         self.planned_duration.append(f'{self.dest_unload_time} hr')
        #                         self.description.append(f'Goods unloading time at {self.route_names_all[i+1]}')
        #                     elif self.dest_unload_time == 0 and i !=len(self.route_names_all)-2:
        #                         self.planned_time.append(self.planned_time[-1] + timedelta(hours=self.entity_origin_loadingtime))  # Fourth entry - Unloading time
        #                         self.planned_location.append(self.route_names_all[i+1])
        #                         self.planned_duration.append(f'{self.entity_origin_loadingtime} hr')
        #                         self.description.append(f'Goods loading time at {self.route_names_all[i+1]}')
        #                     else:
        #                         pass
                                
                            
        #             else:
        #                 pass
                    
        #             self.planned_time = [item.time() for item in self.planned_time]
        #             self.daily_dict = {
        #                 "time": self.planned_time, 
        #                 "location": self.planned_location,
        #                 "duration": self.planned_duration,
        #                 "description": self.description
        #                 }
        #             self.table = pd.DataFrame(self.daily_dict)
        #             self.table = json.loads(self.table.to_json(orient='records'))
        #             self.table_final = {"date": dt.strftime("%d-%m-%Y"), "daily_schedule": self.table}
        #             self.schedules.append(self.table_final)
        
        else:
            pass
        
        
        # For hospital daily allocated quantity
        self.route_daily_hosp_alloc = []
        
        date_temp = [item.strftime("%d-%m-%Y") for item in self.date_range]
        
        for hosp_name in self.route_daily_alloc.index:
            # print(hosp_name)
            quantity_temp = [item for item in self.route_daily_alloc.loc[hosp_name,:]]
            route_daily_alloc_df = pd.DataFrame({ "date": date_temp ,"quantity": quantity_temp})
            self.route_daily_alloc_df = json.loads(route_daily_alloc_df.to_json(orient='records'))
            
            self.daily_alloc = {"destination_name": hosp_name,"daily_alloc": self.route_daily_alloc_df}
            self.route_daily_hosp_alloc.append(self.daily_alloc)
        
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

def retjson(routes_all):
    
    keys_to_extract = [
    'route_daily_hosp_alloc',
    'route_name',
    'route_truck_name',
    'schedules',
    ]
    
    routes_out =[{key: hosp.__dict__[key] for key in keys_to_extract} for hosp in routes_all]
    
    retJSON = {
    "routes": routes_out,
    # "warehouses": warehouse_out,
    # "suppliers": supplier_out,
            }
    return retJSON