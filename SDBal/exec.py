# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 17:09:21 2020

@author: James Ang
"""

import os
os.chdir(r'C:/Users/User/Documents/ghub_acceval/smarttradzt-python-services/SDBal/')

import scipy.stats as ss
import pandas as pd
import copy

excelfilename = 'input_data.xlsx'
rank = pd.read_excel(excelfilename, sheet_name='exec', skiprows = 1, usecols = 'E:J')#.iloc[0,0]

all_ranks = copy.deepcopy(rank)
all_ranks = all_ranks.loc[all_ranks['term_spot'] == "Spot"]

all_ranks['country_cust'] = all_ranks['country_rank'] + all_ranks['customer_rank']
all_ranks['country_prio'] = ss.rankdata(all_ranks['country_cust'], 'dense')

all_ranks['cust_country'] = all_ranks['customer_rank'] + all_ranks['country_rank']
all_ranks['cust_prio'] = ss.rankdata(all_ranks['cust_country'], 'dense')

cut_method = pd.read_excel(excelfilename, sheet_name='exec', skiprows = 0, nrows = 1, usecols = 'N').iloc[0,0]

alloc_to_trim = pd.read_excel(excelfilename, sheet_name='exec', skiprows = 9, nrows = 1, usecols = 'N').iloc[0,0]

#%% By Country
rank_by_country = copy.deepcopy(all_ranks.sort_values(by=['country_prio'],ascending=False))#.reset_index(drop=True)
rank_by_country['Final Allocated Quantity'] = rank_by_country['Forecast']


# Percentage cut tables
country_perctg_cut = pd.read_excel(excelfilename, sheet_name='exec', skiprows = 2, nrows = 4, usecols = 'N:O')#.iloc[0,0]

# Totals
country_total = pd.DataFrame(copy.deepcopy(all_ranks.groupby(['country_rank'])['Forecast'].sum()))
country_total['Percent cut'] = 0
country_total['Max cut qty'] = 0

customer_total = copy.deepcopy(all_ranks.groupby(['country_rank','customer_rank'])['Forecast'].sum())

for i in range(0,len(country_total)):
    if 'A' in country_total.index[i]:
        country_total['Max cut qty'][i] = country_total['Forecast'][i] * 0.01 * country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'A', 'perctg cut']
        country_total['Percent cut'][i] = country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'A', 'perctg cut']
        
    elif 'B' in country_total.index[i]:
        country_total['Max cut qty'][i] = country_total['Forecast'][i] * 0.01 * country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'B', 'perctg cut']
        country_total['Percent cut'][i] = country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'B', 'perctg cut']
        
    elif 'C' in country_total.index[i]:
        country_total['Max cut qty'][i] = country_total['Forecast'][i] * 0.01 * country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'C', 'perctg cut']
        country_total['Percent cut'][i] = country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'C', 'perctg cut']
        
    elif 'D' in country_total.index[i]:
        country_total['Max cut qty'][i] = country_total['Forecast'][i] * 0.01 * country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'D', 'perctg cut']
        country_total['Percent cut'][i] = country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'D', 'perctg cut']
    
    elif 'P' in country_total.index[i]:
        country_total['Max cut qty'][i] = country_total['Forecast'][i] * 0.01 * country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'P', 'perctg cut']
        country_total['Percent cut'][i] = country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'P', 'perctg cut']
        
    else:
        pass

total_max_cut_qty = country_total['Max cut qty'].sum()
country_total['Country'] = pd.DataFrame(copy.deepcopy(all_ranks.groupby(['country_rank'])['ship_to_country'].unique()))
country_total['Country'] = [a[0] for a in country_total['Country']]

#%% Cut Allocation by country
# alloc_to_trim = pd.read_excel(excelfilename, sheet_name='exec', skiprows = 9, nrows = 1, usecols = 'N').iloc[0,0]



if cut_method == 'Country level':
    print('Calculate by Country level')
    
    if alloc_to_trim <= total_max_cut_qty:
        pass
    else:    
        print(f'Allocation Quantity to Trim ({alloc_to_trim} MT) calculated from Supply Demand Plan \
    \nis more than the Total Allowable Trim Quantity ({total_max_cut_qty} MT) set according to Country Trim Percentage.\
    \nTherefore, Maximum Allocation Trim Quantity is set at {total_max_cut_qty} MT.')
        alloc_to_trim = total_max_cut_qty
        
    accumulated_all_country_trimmed_quantity = 0
        
        
    
    # Looping Through Country
    for i in range(len(country_total),0,-1):    # <-- Count backwards because lowest rank to be trimmed first
        
        if accumulated_all_country_trimmed_quantity >= alloc_to_trim:
            print('ALLOCATION PLAN (Country Level) COMPLETED!')
            
            break
        
        accumulated_trimmed_qty = 0
        qty_to_trim = country_total['Max cut qty'][i-1]
        temp_df = copy.deepcopy(rank_by_country.loc[rank_by_country['country_rank'] == country_total.index[i-1], :])
        ind_country = rank_by_country[rank_by_country['country_rank'] == country_total.index[i-1]].index
        
        print('\nCountry: ' + temp_df['ship_to_country'].unique().tolist()[0])
        print('Country Rank: ' + str(country_total.index[i-1]))
        print('Planned Percentage cut: ' + str(country_total['Percent cut'][i-1]) + ' %')
        print('Original Country Allocation: ' + str(country_total['Forecast'][i-1]) + ' MT')
        print(f"Maximum Trim Quantity for {temp_df['ship_to_country'].unique().tolist()[0]} = {qty_to_trim} MT")
        if alloc_to_trim - accumulated_all_country_trimmed_quantity >= qty_to_trim:
            print(f"Quantity to trim for {temp_df['ship_to_country'].unique().tolist()[0]} = {qty_to_trim} MT")
        else:
            print(f"Quantity to trim for {temp_df['ship_to_country'].unique().tolist()[0]} = {alloc_to_trim - accumulated_all_country_trimmed_quantity} MT")
        
        # Looping Through Individual Customers/Companies
        for j in range(0,len(temp_df)):
            
            if accumulated_all_country_trimmed_quantity >= alloc_to_trim:
                print(f"\nEnd of Allocation adjustment for {temp_df['ship_to_country'].unique().tolist()[0]}.")
                print("===================================================================================")
                break
            
            print('\n\tCustomer: ' + str(temp_df['cust_code'].iloc[j]))
            print('\tCustomer rank: ' + str(temp_df['customer_rank'].iloc[j]))
            
            if sum(temp_df['Forecast'][0:j+1]) <= qty_to_trim:
                
                if temp_df['Forecast'].iloc[j] != 0:
                    print('\t\tAA')
                    cut = temp_df['Forecast'].iloc[j]
                    print('\t\tOriginal Allocated Quantity: ' + str(temp_df['Forecast'].iloc[j]) + ' MT')
                    if accumulated_all_country_trimmed_quantity + temp_df['Forecast'].iloc[j] >  alloc_to_trim:
                        cut = alloc_to_trim - accumulated_all_country_trimmed_quantity
                    
                    print(f"\t\tReduce Allocation Quantity by {cut} MT from customer '{temp_df['cust_code'].iloc[j]}'.")
                    accumulated_trimmed_qty+= cut # temp_df['Forecast'].iloc[j]
                    accumulated_all_country_trimmed_quantity += cut #temp_df['Forecast'].iloc[j]
                    print(f"\t\tAccumulated Trimmed Quantity for {temp_df['ship_to_country'].unique().tolist()[0]} = {accumulated_trimmed_qty} MT.")
                    print(f"\t\tAccumulated Trimmed Quantity for All Countries = {accumulated_all_country_trimmed_quantity} MT.")
    
                    rank_by_country.loc[ind_country[j],'Final Allocated Quantity'] = temp_df.loc[ind_country[j],'Forecast'] - cut
                    print(f"\t\tFinal Allocated Quantity: {rank_by_country.loc[ind_country[j],'Final Allocated Quantity']} MT")
                    
                else:
                    print(f"\t\tNothing to Remove from customer '{temp_df['cust_code'].iloc[j]}' from {temp_df['ship_to_country'].iloc[j]}.")
                
            else:
                print('\t\tBB')
                print('\t\tOriginal Allocated Quantity: ' + str(temp_df['Forecast'].iloc[j]) + ' MT')
                
                last_cut =  qty_to_trim - sum(temp_df['Forecast'][0:j])
                
                if accumulated_all_country_trimmed_quantity + last_cut >  alloc_to_trim:
                    last_cut = alloc_to_trim - accumulated_all_country_trimmed_quantity
                
                
                print(f"\t\tReduce Allocation Quantity by {last_cut} MT from customer '{temp_df['cust_code'].iloc[j]}'.")
                accumulated_trimmed_qty+= last_cut
                accumulated_all_country_trimmed_quantity += last_cut
                print(f"\t\tAccumulated Trimmed Quantity for {temp_df['ship_to_country'].unique().tolist()[0]} = {accumulated_trimmed_qty} MT.")
                print(f"\t\tAccumulated Trimmed Quantity for All Countries = {accumulated_all_country_trimmed_quantity} MT.")
                # if accumulated_all_country_trimmed_quantity > alloc_to_trim:
                #     print(f"\t\tQUANTITY IS NOW ABOVE LEVEL! : {accumulated_all_country_trimmed_quantity} MT")
                #     break
                # else:
                    # print(f"\t\tAccumulated Trimmed Quantity for {temp_df['ship_to_country'].unique().tolist()[0]} = {accumulated_trimmed_qty} MT.")
                    # print(f"\t\tAccumulated Trimmed Quantity for All Countries = {accumulated_all_country_trimmed_quantity} MT.")
                    
                rank_by_country.loc[ind_country[j],'Final Allocated Quantity'] = temp_df.loc[ind_country[j],'Forecast'] - last_cut
                print(f"\t\tFinal Allocated Quantity: {rank_by_country.loc[ind_country[j],'Final Allocated Quantity']} MT")
                print(f"\nEnd of Allocation planning for {temp_df['ship_to_country'].unique().tolist()[0]}.")
                print("===================================================================================")
                break

#% By Customer
elif cut_method == 'Customer level':
    
    print('Calculate by Customer level')
    
    rank_by_customer = copy.deepcopy(all_ranks.sort_values(by=['cust_prio'],ascending=False))#.reset_index(drop=True)
    rank_by_customer['Final Allocated Quantity'] = rank_by_customer['Forecast']
    
    # Percentage cut table
    customer_perctg_cut = pd.read_excel(excelfilename, sheet_name='exec', skiprows = 2, nrows = 4, usecols = 'Q:R')#.iloc[0,0]
    
    # Totals
    customer_total = pd.DataFrame(copy.deepcopy(all_ranks.groupby(['customer_rank'])['Forecast'].sum()))
    # customer_total = pd.DataFrame(copy.deepcopy(all_ranks.groupby(['customer_rank', 'country_rank'])['Forecast'].sum()))

    customer_total['Percent cut'] = 0
    customer_total['Max cut qty'] = 0
    
    for i in range(0,len(customer_total)):
        # print(i)
        if 'A' in customer_total.index[i]:
            customer_total['Max cut qty'][i] = customer_total['Forecast'][i] * 0.01 * customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'A', 'cust_perctg cut']
            customer_total['Percent cut'][i] = customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'A', 'cust_perctg cut']
            
        elif 'B' in customer_total.index[i]:
            customer_total['Max cut qty'][i] = customer_total['Forecast'][i] * 0.01 * customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'B', 'cust_perctg cut']
            customer_total['Percent cut'][i] = customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'B', 'cust_perctg cut']
            
        elif 'C' in customer_total.index[i]:
            customer_total['Max cut qty'][i] = customer_total['Forecast'][i] * 0.01 * customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'C', 'cust_perctg cut']
            customer_total['Percent cut'][i] = customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'C', 'cust_perctg cut']
            
        # elif 'D' in customer_total.index[i]:
        #     customer_total['Max cut qty'][i] = customer_total['Forecast'][i] * 0.01 * customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'D', 'cust_perctg cut']
        #     customer_total['Percent cut'][i] = customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'D', 'cust_perctg cut']
        
        elif 'P' in customer_total.index[i]:
            customer_total['Max cut qty'][i] = customer_total['Forecast'][i] * 0.01 * customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'P', 'cust_perctg cut']
            customer_total['Percent cut'][i] = customer_perctg_cut.loc[customer_perctg_cut['customer_rank'] == 'P', 'cust_perctg cut']
            
        else:
            pass
    
    total_max_cut_qty = customer_total['Max cut qty'].sum()

    # customer_total['Country'] = pd.DataFrame(copy.deepcopy(all_ranks.groupby(['customer_rank','country_rank'])['ship_to_country'].unique()))
    # customer_total['Country'] = [a[0] for a in customer_total['Country']]

    if alloc_to_trim <= total_max_cut_qty:
        pass
    else:        
        print(f'Allocation Quantity to Trim ({alloc_to_trim} MT) calculated from Supply Demand Plan \
    \nis more than the Total Allowable Trim Quantity ({total_max_cut_qty} MT) set according to Country Trim Percentage.\
    \nTherefore, Maximum Allocation Trim Quantity is set at {total_max_cut_qty} MT.')
        alloc_to_trim = total_max_cut_qty
    
    accumulated_all_customer_trimmed_quantity = 0
    
    # Looping Through Individual Customers
    
    for i in range(len(customer_total),0,-1):    # <-- Count backwards because lowest rank to be trimmed first
        
        if accumulated_all_customer_trimmed_quantity >= alloc_to_trim:
            print('ALLOCATION PLAN (Customer Level) COMPLETED!')
            
            break

        accumulated_trimmed_qty = 0
        qty_to_trim = customer_total['Max cut qty'][i-1]
        temp_df = copy.deepcopy(rank_by_customer.loc[rank_by_customer['customer_rank'] == customer_total.index[i-1], :])
        ind_customer = rank_by_customer[rank_by_customer['customer_rank'] == customer_total.index[i-1]].index
        
        # print('\nCustomer: ' + temp_df['ship_to_country'].unique().tolist()[0])
        print('Customer Rank: ' + str(customer_total.index[i-1]))
        print('Planned Percentage cut: ' + str(customer_total['Percent cut'][i-1]) + ' %')
        print('Original customer Allocation: ' + str(customer_total['Forecast'][i-1]) + ' MT')
        print(f"Maximum Trim Quantity for Customer Rank {str(customer_total.index[i-1])} = {qty_to_trim} MT")
        
        if alloc_to_trim - accumulated_all_customer_trimmed_quantity >= qty_to_trim:
            print(f"Quantity to trim for {str(customer_total.index[i-1])} = {qty_to_trim} MT")
        else:
            print(f"Quantity to trim for Customer Rank {str(customer_total.index[i-1])} = {alloc_to_trim - accumulated_all_customer_trimmed_quantity} MT")
            
        # Looping Through Individual Countries
        for j in range(0,len(temp_df)):
            
            if accumulated_all_customer_trimmed_quantity >= alloc_to_trim:
                print(f"\nEnd of Allocation adjustment for {str(customer_total.index[i-1])}.")
                print("===================================================================================")
                break
            
            print('\n\tCountry: ' + str(temp_df['ship_to_country'].iloc[j]))
            print('\tCountry rank: ' + str(temp_df['country_rank'].iloc[j]))
            #=================
            if sum(temp_df['Forecast'][0:j+1]) <= qty_to_trim:
                print('\t\tAA')
                if temp_df['Forecast'].iloc[j] != 0:
                    # print('\t\tAA')
                    cut = temp_df['Forecast'].iloc[j]
                    print('\t\tOriginal Allocated Quantity: ' + str(temp_df['Forecast'].iloc[j]) + ' MT')
                    if accumulated_all_customer_trimmed_quantity + temp_df['Forecast'].iloc[j] >  alloc_to_trim:
                        cut = alloc_to_trim - accumulated_all_customer_trimmed_quantity
                    
                    print(f"\t\tReduce Allocation Quantity by {cut} MT from country '{temp_df['ship_to_country'].iloc[j]}'.")
                    accumulated_trimmed_qty+= cut # temp_df['Forecast'].iloc[j]
                    accumulated_all_customer_trimmed_quantity += cut #temp_df['Forecast'].iloc[j]
                    print(f"\t\tAccumulated Trimmed Quantity for Customer Rank {str(customer_total.index[i-1])} = {accumulated_trimmed_qty} MT.")
                    print(f"\t\tAccumulated Trimmed Quantity for All Countries = {accumulated_all_customer_trimmed_quantity} MT.")
    
                    rank_by_customer.loc[ind_customer[j],'Final Allocated Quantity'] = temp_df.loc[ind_customer[j],'Forecast'] - cut
                    print(f"\t\tFinal Allocated Quantity: {rank_by_customer.loc[ind_customer[j],'Final Allocated Quantity']} MT")
                    
                else:
                    print(f"\t\tNothing to Remove from country {temp_df['ship_to_country'].iloc[j]} for customer '{temp_df['cust_code'].iloc[j]}'.")

            else:
                print('\t\tBB')
                print('\t\tOriginal Allocated Quantity: ' + str(temp_df['Forecast'].iloc[j]) + ' MT')
                
                last_cut =  qty_to_trim - sum(temp_df['Forecast'][0:j])
                
                if accumulated_all_customer_trimmed_quantity + last_cut >  alloc_to_trim:
                    last_cut = alloc_to_trim - accumulated_all_customer_trimmed_quantity
                
                
                print(f"\t\tReduce Allocation Quantity by {last_cut} MT from country {temp_df['ship_to_country'].iloc[j]}.")
                accumulated_trimmed_qty+= last_cut
                accumulated_all_customer_trimmed_quantity += last_cut
                print(f"\t\tAccumulated Trimmed Quantity for Customer Rank {str(customer_total.index[i-1])} = {accumulated_trimmed_qty} MT.")
                print(f"\t\tAccumulated Trimmed Quantity for All Countries = {accumulated_all_customer_trimmed_quantity} MT.")
                
                rank_by_customer.loc[ind_customer[j],'Final Allocated Quantity'] = temp_df.loc[ind_customer[j],'Forecast'] - last_cut
                print(f"\t\tFinal Allocated Quantity: {rank_by_customer.loc[ind_customer[j],'Final Allocated Quantity']} MT")
                print(f"\nEnd of Allocation planning Customer Rank {str(customer_total.index[i-1])}.")
                print("===================================================================================")
                break