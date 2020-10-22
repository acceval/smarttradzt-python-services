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

rank1 = copy.deepcopy(rank)
rank1 = rank1.loc[rank1['term_spot'] == "Spot"]

rank1['country_cust'] = rank1['country_rank'] + rank1['customer_rank']
rank1['country_prio'] = ss.rankdata(rank1['country_cust'], 'dense')

rank1['cust_country'] = rank1['customer_rank'] + rank1['country_rank']
rank1['cust_prio'] = ss.rankdata(rank1['cust_country'], 'dense')

rank_by_customer = copy.deepcopy(rank1.sort_values(by=['cust_prio'],ascending=False))#.reset_index(drop=True)
rank_by_country = copy.deepcopy(rank1.sort_values(by=['country_prio'],ascending=False))#.reset_index(drop=True)

cut_method = pd.read_excel(excelfilename, sheet_name='exec', skiprows = 1, nrows = 1, usecols = 'N').iloc[0,0]


# Percentage cut tables
country_perctg_cut = pd.read_excel(excelfilename, sheet_name='exec', skiprows = 2, nrows = 4, usecols = 'N:O')#.iloc[0,0]

company_perctg_cut = pd.read_excel(excelfilename, sheet_name='exec', skiprows = 2, nrows = 4, usecols = 'Q:R')#.iloc[0,0]

# Totals
country_total = pd.DataFrame(copy.deepcopy(rank1.groupby(['country_rank'])['Forecast'].sum()))

country_total['Max cut qty'] = 0
country_total['Percent cut'] = 0

# country_perctg_cut.loc[country_perctg_cut['country_rank'] == 'A', 'perctg cut']

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

company_total = copy.deepcopy(rank1.groupby(['country_rank','customer_rank'])['Forecast'].sum())


#%% Cut Allocation by country

alloc_to_trim = 250

if cut_method == 'country_rank':

    for i in range(len(country_total),0,-1):    # <-- Count backwards because lowest rank to be trimmed first
    
        qty_to_trim = country_total['Max cut qty'][i-1]
        temp_df = rank_by_country.loc[rank_by_country['country_rank'] == country_total.index[i-1], :]
        temp_df['After Trim Qty'] = 0
        
        print('\nCountry: ' + temp_df['ship_to_country'].unique().tolist()[0])
        print('Country Rank: ' + str(country_total.index[i-1]))
        print(f'Planned Percentage cut: ' + str(country_total['Percent cut'][i-1]) + ' %')
        print(f'Original Country Allocation: ' + str(country_total['Forecast'][i-1]) + ' MT')
        print(f'Total Quantity to Reduce = {qty_to_trim} MT')
        
        
        
        for j in range(0,len(temp_df)):
            print('\n\tCustomer: ' + str(temp_df['cust_code'].iloc[j]))
            # print('\t' + str(temp_df['Forecast'].iloc[j]))
            # print('\tsum:' + str(sum(temp_df['Forecast'][0:j+1])))
            
            if sum(temp_df['Forecast'][0:j+1]) <= qty_to_trim:
                
                
                if temp_df['Forecast'].iloc[j] != 0:
                    print('\t\tOriginal Allocated Quantity: ' + str(temp_df['Forecast'].iloc[j]) + ' MT')
                    print('\t\tAccumulated Country Qty:' + str(sum(temp_df['Forecast'][0:j+1])) + ' MT')
                    print(f"\t\tRemove {temp_df['Forecast'].iloc[j]} MT from customer '{temp_df['cust_code'].iloc[j]}'.")
                
                else:
                    print(f"\t\tNothing to Remove from customer '{temp_df['cust_code'].iloc[j]}' from {temp_df['ship_to_country'].iloc[j]}.")
                
            else:
                print('\t\tOriginal Allocated Quantity: ' + str(temp_df['Forecast'].iloc[j]) + ' MT')
                print('\t\tAccumulated Country Qty: ' + str(sum(temp_df['Forecast'][0:j+1])) + ' MT')
                last_cut =  qty_to_trim - sum(temp_df['Forecast'][0:j])
                print(f"\t\tReduce Allocation by {last_cut} MT from customer '{temp_df['cust_code'].iloc[j]}'.")
                print('...End of cutting Allocation.')
                break
                
                
                # if temp_df['customer_rank'][i] == 'P':
                # print(f"Customer {rank_by_customer['cust_code'][i]} is a 'P' ranked customer")
                # print(f"\tRemove {rank_by_customer['Forecast'][i]} MT from customer '{rank_by_customer['cust_code'][i]}' from {rank_by_customer['ship_to_country'][i]}.")

                
        
        # for j in rank_by_country.loc[rank_by_country['country_rank'] == country_total.index[i-1], 'Forecast']:
        #     print('\t'+str(j))
        #     if sum(rank_by_country['Forecast'][0:i+1]) <= alloc_to_trim:
                


for i in range(0,len(rank_by_customer)):
    # print(i)
    
        # print(sum(rank_by_customer['Forecast'][0:i+1]))
        if rank_by_customer['Forecast'][i] != 0:
                        
            if rank_by_customer['customer_rank'][i] == 'P':
                print(f"Customer {rank_by_customer['cust_code'][i]} is a 'P' ranked customer")
                print(f"\tRemove {rank_by_customer['Forecast'][i]} MT from customer '{rank_by_customer['cust_code'][i]}' from {rank_by_customer['ship_to_country'][i]}.")
    
            elif rank_by_customer['customer_rank'][i] == 'C':
                print(f"Customer {rank_by_customer['cust_code'][i]} is a 'C' ranked customer")
                print(f"Remove {rank_by_customer['Forecast'][i]} MT from customer '{rank_by_customer['cust_code'][i]}' from {rank_by_customer['ship_to_country'][i]}.")
    
    else:    
        last_cut = sum(rank_by_customer['Forecast'][0:i+1])- alloc_to_trim
        print(f"Reduce Allocation by {last_cut} MT from customer '{rank_by_customer['cust_code'][i]}' from {rank_by_customer['ship_to_country'][i]}.")
        print('End of cutting Allocation.')
        break