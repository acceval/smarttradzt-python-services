# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:31:30 2020

@author: James Ang
"""
from flask import Flask, request#, jsonify, flash, redirect
from flask_restful import Resource, Api
import sys
import pandas as pd
from truck_lib import Hospital, Truck, Supplier, truck_stat, supp_inv_stat

app = Flask(__name__)
api = Api(app)

#%% Set Upload Folder and Secret Key

if sys.platform == "win32":    
    UPLOAD_FOLDER = r'C:\Users\User\Documents\James\E_BL_LC\LC\alfred\upload'
else:    
    # UPLOAD_FOLDER = r'/home/alfred/uploads'
    UPLOAD_FOLDER = r'/home/alfred/Documents/deploy/lc_bl_inv/uploads'


#%% Endpoint '/' - to test connection

class index(Resource):
    def get(self):
        return request.url

#%% Endpoint '/vaccine_drp'

class truck_schedule(Resource):
    
    def post(self):
        
        data = request.get_json()
        
        data_hospitals = data.get('hospitals')
        #print(data_hospitals)
        num_of_hospitals = len(data_hospitals)
        
        data_supplier = data.get('suppliers')
        #print(data_supplier)
        # num_of_suppliers = len(data_supplier)
        
        data_truck = data.get('trucks')
        num_of_trucks = len(data_truck)
        
        #%%
        trucks = Truck(data_truck)
        hosp_1 = Hospital(data_hospitals, hosp_num = 0)
        order_hosp_1, truck_count_1 = hosp_1.calc()

        hosp_2 = Hospital(data_hospitals, hosp_num = 1)
        order_hosp_2, truck_count_2 = hosp_2.calc()

        hosp_3 = Hospital(data_hospitals, hosp_num = 2)
        order_hosp_3, truck_count_3 = hosp_3.calc()

        hosp_all = [hosp_1, hosp_2, hosp_3]
        hosp_names=[hosp.name for hosp in hosp_all]

        df_order = pd. concat([order_hosp_1, order_hosp_2, order_hosp_3], axis=1)
        df_truck = pd. concat([truck_count_1, truck_count_2, truck_count_3], axis=1)

        # Supplier
        supplier_demand = df_order.sum(axis=1)
        total_truck_count = df_truck.sum(axis=1)

        # Assign trucks
        df_truck_cum_sum = df_truck.cumsum(axis=1)
        for i in reversed(range(1,num_of_hospitals)):

            a = df_truck_cum_sum.iloc[:,i] == df_truck_cum_sum.iloc[:,i-1]
            df_truck_cum_sum.iloc[:,i][a] = 0

        truck_schedule_initial = df_truck_cum_sum.replace([1,2,3],[data_truck[0].get('name'),data_truck[1].get('name'),"Unavailable"])
        truck_schedule_initial.rename(columns={0: hosp_names[0], 1: hosp_names[1], 2: hosp_names[2]},inplace=True)

        supplier = Supplier(data_supplier, supplier_demand, total_truck_count, truck_schedule_initial)


        #%% Optimisation 

        # Step 1 - Find if there are truck clashes
        troubled_truck_index_int, truck_status = truck_stat(total_truck_count,num_of_trucks)

        # Step 2 - Sup Inventory status    
        troubled_sup_inv_value,troubled_sup_inv_index_int, sup_inv_status = supp_inv_stat(supplier.proj_end_inv_initial)

        # What is the number above maximum truck limit?
        # num_truck_above_limit = int(troubled_truck_index) - num_of_trucks

        # Step 3 - Check Pharmaniaga Inventory ok? (at troubled - truck clash)
        if truck_status=="NG":
            if supplier.proj_end_inv[troubled_truck_index_int] < 0:
                supp_inv_status_truck_specific = "NG"
            else:
                supp_inv_status_truck_specific = "OK"
            print(f"Supplier Inventory Truck problem specific status: {supp_inv_status_truck_specific}")
        else:
            supp_inv_status_truck_specific = "OK"

        # Step 4 - Check if previous day total truck is already fully utilised
        if troubled_truck_index_int > 0: # except 1st day

            if total_truck_count[troubled_truck_index_int-1] > num_of_trucks:
                prevday_status = "NG"
            else:
                prevday_status = "OK"
            print(f"Previous day status = {prevday_status}")
        else:
            print('Remove truck or move a day later')

        #%% Scenario 2
        if sup_inv_status == "NG":
            
            prob_type = 2
            
            # STRATEGY - Remove order from hospitals with largest order first until no negative inventory
            qty_to_reduce = -troubled_sup_inv_value
            hosp_orders = [order_hosp_1[troubled_sup_inv_index_int], order_hosp_2[troubled_sup_inv_index_int], order_hosp_3[troubled_sup_inv_index_int]]
            
            while qty_to_reduce[0]>0:
                
                hosp_max_order = max(hosp_orders)
                
                # Which hospital has max quantity?
                hosp_max_order_index = max(range(len(hosp_orders)), key=hosp_orders.__getitem__)
                
                # Remove that quantity so left 0
                hosp_orders[hosp_max_order_index] = 0
                
                # change in respective hospital - cut allocation
                order_hosp_new, truck_count_new = hosp_all[hosp_max_order_index].calc_scen_2(troubled_sup_inv_index_int,prob_type)
                
                df_order.iloc[:,hosp_max_order_index] = order_hosp_new
            
                df_truck.iloc[:,hosp_max_order_index] = truck_count_new
                
                # Check is there balance in qty_to_reduce?
                qty_to_reduce = qty_to_reduce - hosp_max_order
            
            
            # Supplier
            supplier_demand_new = df_order.sum(axis=1)
            total_truck_count_new = df_truck.sum(axis=1)
            
            # supplier = Supplier(data_supplier, supplier_demand, total_truck_count, truck_schedule_initial)
            
            supplier.calc(data_supplier, supplier_demand_new, total_truck_count_new, truck_schedule_initial)
            
            sup_proj_EI_initial = pd.Series(supplier.proj_end_inv_final)
            troubled_sup_inv_value = sup_proj_EI_initial[sup_proj_EI_initial<0]
            troubled_sup_inv_index = sup_proj_EI_initial[sup_proj_EI_initial<0].index
            
            # Check PN Inventory
            if len(troubled_sup_inv_index) == 0:
                sup_inv_status = "OK"
                print(f"Supplier Inv status original: {sup_inv_status}")
            else:
                sup_inv_status = "NG"
                troubled_sup_inv_index_int = sup_proj_EI_initial.index.get_loc(troubled_sup_inv_index[0]) # in integer
                print(f"Supplier Inv status original: {sup_inv_status} at {troubled_sup_inv_index_int}")

            if sup_inv_status == "OK":
                pass
            
                troubled_truck_index_int_scen2, truck_status_scen2 = truck_stat(total_truck_count_new,num_of_trucks)

                


        #%% Solving scenario 1



        # Check previous day hospital projected Inventory - safety stock to see how desperate they are.
        # Choose one with the lowest difference to move, becasue they are most desperate.

        if truck_status=="NG" and supp_inv_status_truck_specific == "OK" and prevday_status == "OK":
            # hosp_all = [hosp_1, hosp_2, hosp_3]
            prob_type = 1
            difference=[hosp.inv_minus_mininv[troubled_truck_index_int-1] for hosp in hosp_all]
            index_min_hosp= min(range(len(difference)), key=difference.__getitem__)
                
            # Moving new truck
            order_hosp_new, truck_count_new = hosp_all[index_min_hosp].calc_scen_1(troubled_truck_index_int,prob_type)
            df_order.iloc[:,index_min_hosp] = order_hosp_new
            
            df_truck.iloc[:,index_min_hosp] = truck_count_new
            
            supplier_demand_new = df_order.sum(axis=1)
            total_truck_count_new = df_truck.sum(axis=1)
            # supplier.calc(data_supplier, supplier_demand_new, total_truck_count_new)
            
        troubled_truck_index_new = total_truck_count_new[total_truck_count_new > num_of_trucks]

        if len(troubled_truck_index_new) == 0:
            truck_status = "OK"
        else:
            truck_status = "NG"
        print(f"Truck status new: {truck_status}")

        # Assign trucks
        df_truck_cum_sum = df_truck.cumsum(axis=1)
        for i in reversed(range(1,num_of_hospitals)):

            a = df_truck_cum_sum.iloc[:,i] == df_truck_cum_sum.iloc[:,i-1]
            df_truck_cum_sum.iloc[:,i][a] = 0

        truck_schedule_final = df_truck_cum_sum.replace([1,2,3],[data_truck[0].get('name'),data_truck[1].get('name'),"Unavailable"])
        truck_schedule_final.rename(columns={0: hosp_names[0], 1: hosp_names[1], 2: hosp_names[2]},inplace=True)
        supplier.calc(data_supplier, supplier_demand_new, total_truck_count_new, truck_schedule_final)

        # Normalising
        hosp_1.normalise()
        hosp_2.normalise()
        hosp_3.normalise()
        supplier.normalise()

        keys_to_extract = [
            'name',
            'table_final'
            # 'net_requirements_safety', 
            #'replenishment_initial', 
            #'replenishment_final' ,
            #'proj_end_inv_initial',
            #'proj_end_inv_final',
            #'truck_count_initial',
            #'truck_count_final'
                        ]
        subset_hosp1 = {key: hosp_1.__dict__[key] for key in keys_to_extract}
        subset_hosp2 = {key: hosp_2.__dict__[key] for key in keys_to_extract}
        subset_hosp3 = {key: hosp_3.__dict__[key] for key in keys_to_extract}
        
        keys_to_extract_supp = [
            'name',
            'table_final',
            # 'net_requirements_safety', 
            #'total_demand_initial',
            #'total_demand_final',
            #'proj_end_inv_initial',
            #'proj_end_inv_final',
            #'total_truck_count_initial',
            #'total_truck_count_final',
            'truck_sched_initial',
            'truck_sched_final'
                           ]
        
        subset_supplier = {key: supplier.__dict__[key] for key in keys_to_extract_supp}

        retJSON = {"hospitals": [
            subset_hosp1, 
            subset_hosp2,
            subset_hosp3,
            ],
            "suppliers": [subset_supplier],
            }
        return retJSON

api.add_resource(index, '/')
api.add_resource(truck_schedule, '/truck_schedule')

if __name__ == '__main__':
    app.run(debug=True)