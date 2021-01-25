# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:25:26 2021

@author: James Ang
"""

import pandas as pd
import operator

def round_to_nearest(num, base):
    n = num + (base//2)
    return n - (n % base)

# class Basic_Data:
    
#     def __init__(self, data):

#         self.state = data.get('state')
#         self.region = data.get('region')
#         self.population = data.get('population')
#         self.overlap_p23 = data.get('overlap_p23')
#         self.basic_alloc_df = pd.DataFrame(data.get('basic_alloc'))
        
# class Vacc_Alloc:
    
#     def __init__(self, data):

#         self.month = data.get('month')
#         self.region = data.get('region')
#         self.state = data.get('state')
#         self.vac_centres_df = pd.DataFrame([item for item in data.get('vac_centres')])
#         self.vac_centres_names = [item.get('name') for item in data.get('vac_centres')]
#         self.vac_centres_types = [item.get('type') for item in data.get('vac_centres')]
#         self.vac_centres_weightedscores = [item.get('weighted_score') for item in data.get('vac_centres')]
#         self.vac_centres_prio_alloc = [item.get('prio_alloc') for item in data.get('vac_centres')]

class Weight_Score:
    
    def __init__(self, data):
        
        self.month = data.get('month')
        self.state = data.get('state')
        self.region = data.get('region')
        self.vac_centre = data.get('vac_centre_name')
        self.weight_score = data.get('weight_score')

class Supplier_Alloc:
    
    def __init__(self, data):

        self.name = data.get('supp_name')
        self.ss_percent = data.get('safety_stock_percent')
        self.dose_per_person = data.get('dose_per_person')
        self.box2dose_conversion = data.get('box_to_dose_conversion')
        self.month = [item.get('month') for item in data.get('monthly_alloc')]
        self.alloc_qty = [item.get('quantity') for item in data.get('monthly_alloc')]
        self.monthly_alloc_df = pd.DataFrame(data.get('monthly_alloc'))
        self.safety_stock = [int(round_to_nearest(item*self.ss_percent/100,self.box2dose_conversion)) for item in self.alloc_qty]
        self.monthly_alloc_df['safety_stock'] = self.safety_stock
        self.avail_supp_inv = list(map(operator.sub, self.alloc_qty, self.safety_stock))
        self.monthly_alloc_df['available_supply_inv_doses'] = self.avail_supp_inv
        self.monthly_alloc_df['available_supply_inv_boxes'] = [int(item/self.box2dose_conversion) for item in self.avail_supp_inv]


class Calc_Month:
    
    def __init__(self, data_basic, data_valloc, data_supplier):
        
        # Basic Data
        self.basic_df = pd.DataFrame(data_basic)
        self.population = [item.get('population') for item in data_basic]
        self.total_population = sum(self.population)
        # self.population = [item.population for item in basic]
        self.region_basic = [item.get('region') for item in data_basic]
        # self.region_basic = [item.region for item in basic]
        self.state_basic = [item.get('state') for item in data_basic]
        # self.state_basic = [item.state for item in basic]
        self.overlap_p23_basic = [item.get('overlap_p23') for item in data_basic]
        # self.overlap_p23_basic = [item.overlap_p23 for item in basic]
        
        self.priority1_basic = [int(pd.DataFrame(item.get('basic_alloc'))['num_persons'][pd.DataFrame(item.get('basic_alloc'))['priority'] == 1]) for item in data_basic]
        # self.priority1_basic = [int(item.basic_alloc_df['num_persons'][item.basic_alloc_df['priority'] ==1]) for item in basic]
        self.priority2_basic = [int(pd.DataFrame(item.get('basic_alloc'))['num_persons'][pd.DataFrame(item.get('basic_alloc'))['priority'] == 2]) for item in data_basic]
        # self.priority2_basic = [int(item.basic_alloc_df['num_persons'][item.basic_alloc_df['priority'] ==2]) for item in basic]
        self.priority3_basic = [int(pd.DataFrame(item.get('basic_alloc'))['num_persons'][pd.DataFrame(item.get('basic_alloc'))['priority'] == 3]) for item in data_basic]
        # self.priority3_basic = [int(item.basic_alloc_df['num_persons'][item.basic_alloc_df['priority'] ==3]) for item in basic]
        self.priority4_basic = [int(pd.DataFrame(item.get('basic_alloc'))['num_persons'][pd.DataFrame(item.get('basic_alloc'))['priority'] == 4]) for item in data_basic]
        # self.priority4_basic = [int(item.basic_alloc_df['num_persons'][item.basic_alloc_df['priority'] ==4]) for item in basic]

        # Vaccine Allocation
        self.valloc_df = pd.DataFrame(data_valloc)
        self.merged = pd.merge(self.valloc_df,self.basic_df[['state', 'region', 'overlap_p23']], on=['state', 'region'], how='left')
        # self.merged = pd.merge(self.basic_df, self.valloc_df, on=['state', 'region'])
        self.month_valloc = [item.get('month') for item in data_valloc]
        self.state_valloc = [item.get('state') for item in data_valloc]
        self.region_valloc = [item.get('region') for item in data_valloc]
        self.region_vac_centres_valloc = [item.get('vac_centres') for item in data_valloc]
        
        # Supplier Data
        self.supplier_df = pd.DataFrame(data_supplier)
        
        # Calc
        self.names_valloc = []
        self.types_valloc = []
        self.total_people_valloc = []
        self.total_doses_valloc = []
        
        for i in self.merged.index:
            
            # Getting overlap for each respective state+region
            overlap_23 = self.merged['overlap_p23'][i]
            
            for item in self.merged['vac_centres'][i]:
                
                self.names_valloc.append(item.get('name'))
                self.types_valloc.append(item.get('type'))
                vaccine_type = item.get('vaccine_type')
                box2dose = int(self.supplier_df['box_to_dose_conversion'][self.supplier_df['supp_name'] == vaccine_type])
                dose_per_person = int(self.supplier_df['dose_per_person'][self.supplier_df['supp_name'] == vaccine_type])
                
                if item.get('type') == "hospital":
                    
                    alloc_hospital = sum([item3.get('num_people') for item3 in item.get('prio_alloc')])-overlap_23
                    self.total_people_valloc.append(alloc_hospital)
                    overlap_23 = 0
                    self.total_doses_valloc.append(round_to_nearest(alloc_hospital*dose_per_person,box2dose))
                    
                elif item.get('type') == "clinic":
                    self.total_people_valloc.append(0)
                    self.total_doses_valloc.append(0)
                    
                else:
                    alloc_elderly = sum([item3.get('num_people') for item3 in item.get('prio_alloc')])
                    self.total_people_valloc.append(alloc_elderly)
                    self.total_doses_valloc.append(alloc_elderly*dose_per_person)
        # for item in self.region_vac_centres_valloc:
            
            
        #     for item2 in item:
        #         self.names_valloc.append(item2.get('name'))
        #         self.types_valloc.append(item2.get('type'))
        #         self.total_people_valloc.append(sum([item3.get('num_people') for item3 in item2.get('prio_alloc')]))