# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:25:26 2021

@author: James Ang
"""

import pandas as pd
import operator
import copy
import numpy as np

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
        
        self.priority1_basic = [int(pd.DataFrame(item.get('basic_alloc'))['num_persons']\
                                    [pd.DataFrame(item.get('basic_alloc'))['priority'] == 1]) for item in data_basic]
        # self.priority1_basic = [int(item.basic_alloc_df['num_persons'][item.basic_alloc_df['priority'] ==1]) for item in basic]
        self.priority2_basic = [int(pd.DataFrame(item.get('basic_alloc'))['num_persons']\
                                    [pd.DataFrame(item.get('basic_alloc'))['priority'] == 2]) for item in data_basic]
        # self.priority2_basic = [int(item.basic_alloc_df['num_persons'][item.basic_alloc_df['priority'] ==2]) for item in basic]
        self.priority3_basic = [int(pd.DataFrame(item.get('basic_alloc'))['num_persons']\
                                    [pd.DataFrame(item.get('basic_alloc'))['priority'] == 3]) for item in data_basic]
        # self.priority3_basic = [int(item.basic_alloc_df['num_persons'][item.basic_alloc_df['priority'] ==3]) for item in basic]
        self.priority4_basic = [int(pd.DataFrame(item.get('basic_alloc'))['num_persons']\
                                    [pd.DataFrame(item.get('basic_alloc'))['priority'] == 4]) for item in data_basic]
        # self.priority4_basic = [int(item.basic_alloc_df['num_persons'][item.basic_alloc_df['priority'] ==4]) for item in basic]
        self.total_basic_checksum = sum(self.priority1_basic) +\
                            sum(self.priority2_basic) +\
                                sum(self.priority3_basic) +\
                                    sum(self.priority4_basic) -\
                                        sum(self.overlap_p23_basic)
        print(f"Total number persons basic data = {self.total_basic_checksum} persons")

        # Vaccine Allocation
        self.valloc_df = pd.DataFrame(data_valloc)
        self.merged = pd.merge(self.valloc_df,self.basic_df[['state', 'region', 'overlap_p23','basic_alloc']], on=['state', 'region'], how='left')

        self.priority1_valloc = [int(pd.DataFrame(item.get('basic_alloc'))['num_persons']\
                                    [pd.DataFrame(item.get('basic_alloc'))['priority'] == 1]) for item in data_basic]
        self.month_valloc = [item.get('month') for item in data_valloc]
        self.state_valloc = [item.get('state') for item in data_valloc]
        self.region_valloc = [item.get('region') for item in data_valloc]
        self.region_vac_centres_valloc = [item.get('vac_centres') for item in data_valloc]
        
        # Supplier Data
        self.supplier_df = pd.DataFrame(data_supplier)
        
        # Calc
        self.names_valloc = []
        self.types_valloc = []
        self.initial_valloc_dose = []
        self.final_valloc_dose = []
        self.rounded_up_boxes = []
        self.remaining_not_vaccinated = []
        self.balance_vac_by_vc = []
        self.merged_1 = []
        self.balance_adult_population = []
        self.region_vaccinated = []

        for i in self.merged.index:     # By State+region
            # print(i)
            
            # Getting overlap for each respective state+region
            overlap_23 = self.merged['overlap_p23'][i]
            basic_table_df = pd.DataFrame(self.merged['basic_alloc'][i]).sort_values(by=['priority'],ascending=True)
            if overlap_23 !=0:
                basic_table_df['num_persons'][basic_table_df['priority'] ==3] =\
                    basic_table_df['num_persons'][basic_table_df['priority'] ==3] - overlap_23
            else:
                pass
            
            # Prepare new table for merging basic and allocated data
            merged_basic_valloc = copy.deepcopy(basic_table_df)
            merged_basic_valloc.rename(columns={'num_persons': 'num_persons_basic'}, inplace=True)
            merged_basic_valloc['num_persons_valloc'] = 0
            merged_basic_valloc['Cut qty'] = 0
            merged_basic_valloc['num_persons_remaining'] = merged_basic_valloc['num_persons_basic']
            # merged_basic_valloc.set_index('priority',inplace=True)
            
            for item in self.merged['vac_centres'][i]:  # by vaccine centres (13)
                
                self.names_valloc.append(item.get('name'))
                self.types_valloc.append(item.get('type'))
                vaccine_type = item.get('vaccine_type')
                box2dose = int(self.supplier_df['box_to_dose_conversion'][self.supplier_df['supp_name'] == vaccine_type])
                dose_per_person = int(self.supplier_df['dose_per_person'][self.supplier_df['supp_name'] == vaccine_type])
                
                if item.get('type') == "hospital":
                    
                    prio_alloc_df = pd.DataFrame(item.get('prio_alloc')).sort_values(by=['priority'],ascending=True)
                    prio_alloc_df.rename(columns={'num_persons': 'num_persons_valloc'}, inplace=True)
                    merged_basic_valloc.set_index('priority',inplace=True)
                    merged_basic_valloc.update(prio_alloc_df.set_index('priority'))
                    merged_basic_valloc.reset_index(inplace=True)
                    # Merge basic and valloc
                    # merged_basic_valloc = pd.merge(basic_table_df, prio_alloc_df, on=['priority'], how='left')
                    # merged_basic_valloc['num_persons_valloc'] = merged_basic_valloc['num_persons_valloc'].fillna(0)
                    merged_basic_valloc[['num_persons_valloc','Cut qty']] =\
                        merged_basic_valloc[['num_persons_valloc','Cut qty']].astype(int)
                    # merged_basic_valloc.dtypes
                    
                    # Initial Alloc Hospital
                    initial_alloc = int(merged_basic_valloc['num_persons_valloc'].sum())
                    self.initial_valloc_dose.append(initial_alloc)
                    
                    final_alloc_rounded = round_to_nearest(initial_alloc,box2dose)
                    # overlap_23 = 0  # Reset to 0
                    self.final_valloc_dose.append(final_alloc_rounded)
                    
                    amount_to_cut = copy.deepcopy(final_alloc_rounded)
                    
                    for k in range(0,len(merged_basic_valloc)):
                        # if merged_basic_valloc['priority'][k] == 1:   #priority 1

                        if amount_to_cut >= merged_basic_valloc['num_persons_valloc'][k]\
                            and merged_basic_valloc['num_persons_valloc'][k] !=0:
                            
                            amount_to_cut = amount_to_cut - merged_basic_valloc['num_persons_valloc'][k]
                            merged_basic_valloc.loc[k,'num_persons_remaining'] =\
                                merged_basic_valloc.loc[k,'num_persons_remaining']\
                                    - merged_basic_valloc['num_persons_valloc'][k]
                            merged_basic_valloc.loc[k, 'Cut qty'] = merged_basic_valloc.loc[k, 'Cut qty']\
                                + merged_basic_valloc.loc[k,'num_persons_valloc']
                            merged_basic_valloc.loc[k,'num_persons_valloc'] = 0
                        
                        elif amount_to_cut < merged_basic_valloc['num_persons_valloc'][k]\
                            and merged_basic_valloc['num_persons_valloc'][k] !=0:
                            merged_basic_valloc.loc[k,'num_persons_remaining'] =\
                                merged_basic_valloc.loc[k,'num_persons_remaining'] - amount_to_cut
                            merged_basic_valloc.loc[k, 'Cut qty'] = merged_basic_valloc.loc[k, 'Cut qty']\
                                + amount_to_cut
                            amount_to_cut = amount_to_cut - merged_basic_valloc['num_persons_valloc'][k]
                            merged_basic_valloc.loc[k,'num_persons_valloc'] = 0#merged_basic_valloc.loc[k,'num_persons_valloc'] - amount_to_cut
                            
                        else:# merged_basic_valloc['num_persons_valloc'][k] ==0:
                            pass

                    if initial_alloc-final_alloc_rounded<0:
                        self.remaining_not_vaccinated.append(0)
                        self.balance_vac_by_vc.append(final_alloc_rounded - initial_alloc)
                    else:
                        self.remaining_not_vaccinated.append(initial_alloc-final_alloc_rounded)
                        self.balance_vac_by_vc.append(0)
                        
                    self.rounded_up_boxes.append(round(final_alloc_rounded/box2dose,1)) #= [round(item/box2dose,1) for item in self.final_valloc_dose]
                    
                    # self.final_valloc_dose.append(round_to_nearest(initial_alloc*dose_per_person,box2dose))
                    
                elif item.get('type') == "clinic":
                    self.initial_valloc_dose.append(0)
                    self.final_valloc_dose.append(0)
                    self.rounded_up_boxes.append(0)
                    self.remaining_not_vaccinated.append(0)
                    self.balance_vac_by_vc.append(0)
                    
                else:
                    prio_alloc_df = pd.DataFrame(item.get('prio_alloc')).sort_values(by=['priority'],ascending=True)
                    prio_alloc_df.rename(columns={'num_persons': 'num_persons_valloc'}, inplace=True)
                    merged_basic_valloc.set_index('priority',inplace=True)
                    merged_basic_valloc.update(prio_alloc_df.set_index('priority'))
                    merged_basic_valloc.reset_index(inplace=True)
                    # Merge basic and valloc
                    merged_basic_valloc[['num_persons_valloc','Cut qty']] =\
                        merged_basic_valloc[['num_persons_valloc','Cut qty']].astype(int)

                    
                    # Initial Alloc Elderly Care Homes
                    initial_alloc = int(merged_basic_valloc['num_persons_valloc']\
                                        [merged_basic_valloc['priority']==2].sum())
                    self.initial_valloc_dose.append(initial_alloc)
                    
                    # Final Alloc Elderly Care Homes
                    final_alloc_rounded = copy.deepcopy(initial_alloc)
                    self.final_valloc_dose.append(final_alloc_rounded)
                    
                    amount_to_cut = copy.deepcopy(final_alloc_rounded)
                    
                    for k in range(0,len(merged_basic_valloc)):

                        if amount_to_cut >= merged_basic_valloc['num_persons_valloc'][k]\
                            and merged_basic_valloc['num_persons_valloc'][k] !=0:
                            
                            amount_to_cut = amount_to_cut - merged_basic_valloc['num_persons_valloc'][k]
                            
                            merged_basic_valloc.loc[k,'num_persons_remaining'] =\
                                merged_basic_valloc.loc[k,'num_persons_remaining']\
                                    - merged_basic_valloc['num_persons_valloc'][k]
                            
                            merged_basic_valloc.loc[k, 'Cut qty'] = merged_basic_valloc.loc[k, 'Cut qty']\
                                + merged_basic_valloc.loc[k,'num_persons_valloc']
                            
                            merged_basic_valloc.loc[k,'num_persons_valloc'] = 0
                        
                        else:
                            amount_to_cut = amount_to_cut - merged_basic_valloc['num_persons_valloc'][k]
                    
                    # self.merged_1.append(merged_basic_valloc)
                    
                    # alloc_elderly = sum([item3.get('num_persons') for item3 in item.get('prio_alloc')])
                    # self.initial_valloc_dose.append(alloc_elderly)
                    # self.final_valloc_dose.append(alloc_elderly)
                    self.rounded_up_boxes.append(round(final_alloc_rounded/box2dose,1))
                    self.remaining_not_vaccinated.append(0)
                    self.balance_vac_by_vc.append(0)
                    # self.final_valloc_dose.append(alloc_elderly*dose_per_person)
            self.merged_1.append(copy.deepcopy(merged_basic_valloc))
            self.balance_adult_population.append(sum(merged_basic_valloc['num_persons_remaining']))
            self.region_vaccinated.append(sum(merged_basic_valloc['Cut qty']))
        # Settle for clinic
        
        total_check = [a+b for a,b in zip(self.region_vaccinated,self.balance_adult_population)]
        # self.rounded_up_boxes = [round(item/box2dose,1) for item in self.final_valloc_dose]
        print(f"Total Initial Planned Vaccine Allocation = {sum(self.initial_valloc_dose)} doses")
        print(f"Total Final Planned Vaccine Allocation = {sum(self.final_valloc_dose)} doses")
        print(f"Number of Planned Leftover Persons Not vaccinated (by Vaccine Centres) = {self.remaining_not_vaccinated} persons")
        print(f"Planned Balance Doses (by Vaccine Centres) = {self.balance_vac_by_vc} doses")
        print(f"Number of Planned Vaccinations (by Region) = {self.region_vaccinated} persons")
        print(f"Total Country Planned Vaccinations = {sum(self.region_vaccinated)} persons")
        print(f"Planned Balance Adult Population Not Vaccinated (by Region) = {self.balance_adult_population} persons")
        print(f"Total Country Planned Balance Adult Population Not Vaccinated  = {sum(self.balance_adult_population)} persons")
        print(f"Total Check = {total_check}")
        
        
