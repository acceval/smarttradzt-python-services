# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 08:20:05 2020

@author: James Ang
"""

import json
import math
import copy
from datetime import datetime, timedelta
import pandas as pd


def round_down(num, divisor):
    return num - (num%divisor)

class Container:
    
    def __init__(self, data):
        
        self.data = data
        # self.name = self.data.get('name')
        self.num_of_box = data.get('numberOfBox')
        # self.containerType
        # self.id
        # self.innerDimension
        # self.new
        # self.numberOfBox
        # self.outerDimension
        # self.temperatureRange
        # self.volume
        # self.weight

class Allocation:
    
    def __init__(self, data, containers):
        
        self.data = data
        self.origin_country = data.get('from')
        if self.origin_country == "Germany":
            self.origin_airport = "Munich International Airport"
        else:
            pass
        
        self.destination_country = data.get('to')
        
        if self.destination_country == "Malaysia":
            self.destination_airport = "Kuala Lumpur International Airport"
        elif self.destination_country == "UK":
            self.destination_airport = "London Heathrow Airport"
        else:
            pass
        
        self.allocation = data.get('allocation')
        self.month = [item.get('month') for item in self.allocation]
        self.quantity = [item.get('quantity') for item in self.allocation]
        
        conversion_box_to_dose = 4875
        self.quantity_in_boxes = [item/conversion_box_to_dose for item in self.quantity]
        
        # Containers info
        self.container_numofbox = [cont.num_of_box for cont in containers]
        self.container_numofbox_sorted = [cont.num_of_box for cont in containers]
        self.container_numofbox_sorted.sort()
        self.containers_data = [cont.data for cont in containers]
        
        
        # Get delivery dates based on month
        self.format_date = "%b-%Y"
        self.dt_list = [datetime.strptime(dt, self.format_date) for dt in self.month]
        # self.dt_list = [datetime.strptime(dt, self.format_date) for dt in self.month]
        
        self.weekly_delivery_dates = []
        self.num_of_deliverydays_inmonth = []
        
        
        for start_date in self.dt_list:
            
            next_month = start_date.replace(day=28) + timedelta(days=4)
            last_date = next_month - timedelta(days=next_month.day)
            print(last_date)
            date_range_month =pd.date_range(start=start_date, end=last_date, 
                         freq='W-THU').strftime('%m/%d/%Y').tolist()
            self.weekly_delivery_dates.append(date_range_month)
            self.num_of_deliverydays_inmonth.append(len(date_range_month))
        
        # Find allocation and divide to weeks
        
        self.container_types_all =[]
        self.container_types_max_all =[]
        self.weekly_qty = []
        
        for i in range(0,len(self.month)):
            
            self.rounded_qty_per_month = round_down(self.quantity_in_boxes[i],self.num_of_deliverydays_inmonth[i])
            self.qty_per_week = self.rounded_qty_per_month/self.num_of_deliverydays_inmonth[i]
            remainder =  self.quantity_in_boxes[i]-self.rounded_qty_per_month
            
            qty_per_week_list = [self.qty_per_week]*self.num_of_deliverydays_inmonth[i]
            
            if remainder > 0:
                for j in range(0,int(remainder)):

                    qty_per_week_list[j] = qty_per_week_list[j] + 1
                
                
            self.weekly_qty.append(copy.deepcopy(qty_per_week_list))
            
            # if weekly qty above max container size qty, minus the max container size.
            max_cont_size = max(self.container_numofbox_sorted)
            
            container_max_needed = [0]*self.num_of_deliverydays_inmonth[i]
            container_max_size = [max_cont_size]*self.num_of_deliverydays_inmonth[i]
            
            
            for k in range(0,len(qty_per_week_list)):
                
                while qty_per_week_list[k] > max_cont_size:
                    qty_per_week_list[k] = qty_per_week_list[k] - max_cont_size
                    container_max_needed[k]=container_max_needed[k] +1
            
            cont_max_need = copy.deepcopy(container_max_needed)
            
            # After removing amount so that remaining quantity is less than max container size
            self.chosen_container_size_month = []
            for qty in qty_per_week_list:
                print(qty)
                
                for container_size in self.container_numofbox_sorted:

                    if qty < container_size:
                        
                        self.chosen_container_size_month.append(container_size)
                        print(f"Container chosensize is : {self.chosen_container_size_month}")
                        break
            
            
            self.container_type_max = []
            
            if not all(v == 0 for v in cont_max_need):
                print("Needed additional container")
                
                for l in range(0,len(container_max_size)):
                    # print(l)
                    chosen_container = container_max_size[l]
                # for chosen_container in container_max_size:
                    # print(chosen_container)
                    self.container_index = self.container_numofbox.index(chosen_container)
                    self.container_type_max.append(containers[self.container_index].data)
                    self.container_type_max[0]['container_type_quantity'] = cont_max_need[l]
            
                self.container_types_max_all.append(copy.deepcopy(self.container_type_max))
            
            else:
                # self.container_type_max.append(containers[self.container_index].data)
                pass
            
            self.container_type = []
            for chosen_container in self.chosen_container_size_month:
                # print(chosen_container)
                self.container_index = self.container_numofbox.index(chosen_container)
                self.container_type.append(containers[self.container_index].data)
                self.container_type[0]['container_type_quantity'] = 1
        
            self.container_types_all.append(self.container_type)
            

        # Combining lists
        self.container_max_info = [j for i in self.container_types_max_all for j in i]
        self.container_info = [j for i in self.container_types_all for j in i]
        self.combined_deliverydates = [j for i in self.weekly_delivery_dates for j in i]
        self.weekly_quantity = [j for i in self.weekly_qty for j in i]

        if not all(v == 0 for v in cont_max_need):
            b = [[i , j] for i, j in zip(self.container_info, self.container_max_info)]
            # print("yes max")
        else:
            b = [[item] for item in self.container_info]
            # print("no max")
        
        self.format_date1 = "%m/%d/%Y"
        ETA = [datetime.strptime(dt, self.format_date1) + timedelta(days=1) for dt in self.combined_deliverydates]
        self.ETA = [dt.strftime('%m/%d/%Y') for dt in ETA]
        
        self.container_type_qty_and_schedule = pd.DataFrame({'container_info':b,'ETA': self.ETA, 'ETD':self.combined_deliverydates, "weekly_allocated_quantity":self.weekly_quantity })
        self.container_type_qty_and_schedule = json.loads(self.container_type_qty_and_schedule.to_json(orient='records'))

def retjson(allocation_all):
    
    keys_to_extract = [
        'origin_country',
        'destination_country',
        'destination_airport',
        'container_type_qty_and_schedule',
        ]
        
    allocation_out =[{key: item.__dict__[key] for key in keys_to_extract} for item in allocation_all]
    
    
    retJSON = {"airfreight_schedule": allocation_out,
                # "warehouses": warehouse_out,
                # "suppliers": supplier_out,
                # "dryice_suppliers": dryice_out
                }
    
    return retJSON