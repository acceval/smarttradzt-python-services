# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 15:14:18 2020

@author: User
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
from random import seed
import random

data = pd.read_excel(r'C:/Users/User/Documents/James/Infineon_Challenge/MEG Sales Contract 20200528 v1.xlsx')
data = data[{
    'Contract Execution Date', 
    # 'PMT No.', 
    'Item No', 
    'Sales Contract No.',
    'Contract/Spot', 
    # 'Category', 
    # 'Term Type', 
    'Sold to Customer Name',
    # 'Sold to Customer Code', 
    'Customer Type', 
    'Customer Industry', 
    # 'Grade',
    # 'Material', 
    'Country', 
    'Incoterm', 
    'Payment Term', 
    'Destination Port',
    # 'City State', 
    'Shipping Condition', 
    'Plant', 
    # 'RETA', 
    # 'BL Date',
    'EXCHANGE_RATE', 
    'QUANTITY', 
    # 'UOM', 
    'Currency', 
    'FLOOR_PRICE',
    'NORMALISED_INVOICE_PRICE', 
    # 'AVGPUBLISHEDPRICE', 
    'GRADEALPHA', 
    # 'ALPHA2',
    # 'INVOICEPRICE'
    }]

data = data[data['Contract/Spot'] =='QUOTATION']

# Select data  with only USD
data = data[data['Currency'] =='USD']

data = data.reset_index(drop=True)

# Removing rows with Nans
data = data.dropna()

#%% Import invoice data
data2 = pd.read_excel(r'C:/Users/User/Documents/James/Infineon_Challenge/MEG Invoice 20200528 v1.xlsx')
data2 = data2[data2['Contract/Spot'] =='Spot']

# Removing rows with Nans
data2 = data2.dropna()

#%% Join both data
data3 = pd.merge(data, data2, left_on='Sales Contract No.', right_on='SAP Sales Contract ID',how='inner')

# a=data3['PO Date'] - data3['Contract Execution Date']
# max(a)

#%% Check similarities
compare =data3['Contract Execution Date'] == data3['PO Date']
if all(compare) ==True:
    data3.drop('PO Date', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]
    data3 = data3[compare == True]
    data3.drop('PO Date', axis=1, inplace = True)
print(all(compare))
print(np.sum(compare))

"OK"
compare =data3['Customer Type_x'] == data3['Customer Type_y']
if all(compare) ==True:
    data3.drop('Customer Type_y', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]
    data3 = data3[compare == True]
    data3.drop('Customer Type_y', axis=1, inplace = True)
print(all(compare))
print(np.sum(compare))
# np.count_nonzero(compare)

compare =data3['Country_x'] == data3['Country_y']
if all(compare) ==True:
    data3.drop('Country_y', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]
    # data3 = data3[compare == True]
    data3.drop('Country_y', axis=1, inplace = True)
print(all(compare))
print(np.sum(compare))

compare =data3['Contract/Spot_x'] == data3['Contract/Spot_y']
data_dif = data3[compare == False]
print(all(compare))
print(np.sum(compare))
data3['Contract/Spot_x'].unique()
data3['Contract/Spot_y'].unique()
data3.drop('Contract/Spot_x', axis=1, inplace = True)
data3.drop('Contract/Spot_y', axis=1, inplace = True)

compare = data3['Payment Term_x'] == data3['Payment Term_y']
if all(compare) ==True:
    data3.drop('Payment Term_y', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]
    data3 = data3[compare == True]
    data3.drop('Payment Term_y', axis=1, inplace = True)
print(all(compare))
print(np.sum(compare))

compare =data3['Sold to Customer Name'] == data3['Sold To Customer Name']
if all(compare) ==True:
    data3.drop('Sold To Customer Name', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]
    data3 = data3[compare == True]
print(all(compare))
print(np.sum(compare))

compare =data3['Customer Industry_x'] == data3['Customer Industry_y']
if all(compare) ==True:
    data3.drop('Customer Industry_y', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]

print(all(compare))
print(np.sum(compare))

compare =data3['Plant_x'] == data3['Plant_y']
if all(compare) ==True:
    data3.drop('Plant_y', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]
    data3 = data3[compare == True]
    data3.drop('Plant_y', axis=1, inplace = True)
print(all(compare))
print(np.sum(compare))

compare =data3['Incoterm_x'] == data3['Incoterm_y']
if all(compare) ==True:
    data3.drop('Incoterm_y', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]
    data3 = data3[compare == True]
    data3.drop('Incoterm_y', axis=1, inplace = True)
print(all(compare))
print(np.sum(compare))

compare =data3['FLOOR_PRICE'] == data3['Floor Price (USD/MT)']
if all(compare) ==True:
    data3.drop('Floor Price (USD/MT)', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]
    # data3 = data3[compare == True]
    # data3.drop('Floor Price (USD/MT)', axis=1, inplace = True)
print(all(compare))
print(np.sum(compare))

compare =data3['Average Market Price'] == data3['Market Pub Price(USD/MT)']
if all(compare) ==True:
    data3.drop('Market Pub Price(USD/MT)', axis=1, inplace = True)
else:
    data_dif = data3[compare == False]
    # data3 = data3[compare == True]
    data3.drop('Market Pub Price(USD/MT)', axis=1, inplace = True)
print(all(compare))
print(np.sum(compare))

np.sum(data3['Currency'] =='USD')
data3.drop('Currency', axis=1, inplace = True)
data3.drop('Invoice No', axis=1, inplace = True)
data3.drop('RECORDID', axis=1, inplace = True)
data3.drop('SAP Sales Contract ID', axis=1, inplace = True)
data3.drop('EXCHANGE_RATE', axis=1, inplace = True)
data3.drop('Shipping Condition_x', axis=1, inplace = True)
data3.drop('PMT Document ID', axis=1, inplace = True)
data3.drop('PMT No', axis=1, inplace = True)
data3.drop('QUANTITY', axis=1, inplace = True)
data3.drop('Sold To Customer Code', axis=1, inplace = True)
data3.drop('Material', axis=1, inplace = True)
data3.drop('Grade', axis=1, inplace = True)
data3.drop('Destination Port_y', axis=1, inplace = True)
data3.drop('Country_x', axis=1, inplace = True)
data3.drop('Value(USD)', axis=1, inplace = True)
data3.drop(['NORMALISED_INVOICE_PRICE','FLOOR_PRICE', 'GRADEALPHA','Average Market Price', 'Normal IP(MKT)(USD/MT)',
       'Premium over Pub(USD/MT)', 'Invoice Price(USD/MT)','Invoice Item No','PMT Document Item ID',
       'Floor Price (USD/MT)', 'Normalised Invoice Price (ctn)','Sales Contract No.', 'Item No',
       'Baseline Price Premium'], axis=1, inplace = True)

data3 = data3.reset_index(drop=True)
#%% Modifying data
# seed random number generator
seed(1)
random.choices(np.arange(1, 8),k=10)

data3['ori_lead_time'] = 3
data3.loc[data3['Shipping Condition_y'] =='MI','ori_lead_time'] = 8
data3.loc[data3['Shipping Condition_y'] =='MB','ori_lead_time'] = 8

# Labeling
data3['cust_type'] = 'Normal'

# Group 1 - date_changer
G1 = [
      'AIK MOH PAINTS & CHEMICALS PTE LTD',
      'FACI ASIA PACIFIC PTE LTD',
      'SINGAPORE HIGHPOLYMER CHEMICAL',
      ]
# Group 2 - Quan_changer_small
G2 = [
      'HEXTAR CHEMICALS SDN BHD',
      'HIGHPOLYMER CHEMICAL PRODUCTS (M)',
      'SAMCHEM SDN. BHD.'
      ]

# Group 3 - Quan_changer_large
G3 = [
      'SINOPEC CHEMICAL COMMERCIAL HOLDING',
      'GC GLYCOL COMPANY LIMITED',
      'HELM KOREA LTD.'
      ]

# Group 4 - Date_changer_critical
G4 = [
      'TORAY INTERNATIONAL, INC.',
      'MITSUBISHI CORPORATION',
      'TOYOTA TSUSHO ASIA PACIFIC PTE. LTD',
      ]

data3['order_times_changed'] = 0
data3['new_lead_time'] = data3['ori_lead_time']
for comp in G1:
    data3.loc[data3['Sold to Customer Name'] ==comp,'order_times_changed'] = random.choices(np.arange(1,4), k= np.sum(data3['Sold to Customer Name'] ==comp))
    data3.loc[data3['Sold to Customer Name'] ==comp,'new_lead_time'] = random.choices(np.arange(1, 8),k= np.sum(data3['Sold to Customer Name'] ==comp))
    data3.loc[data3['Sold to Customer Name'] ==comp,'cust_type'] = 'date_changer'

data3['Quan_amt_changed'] = 0
data3['Final_quan'] = data3['Quantity (MT)']
for comp in G2:
    a=random.choices(np.arange(10,51,10),k=np.sum(data3['Sold to Customer Name'] ==comp))
    data3.loc[data3['Sold to Customer Name'] ==comp,'Quan_amt_changed'] = a
    data3.loc[data3['Sold to Customer Name'] ==comp,'Final_quan'] = data3.loc[data3['Sold to Customer Name'] ==comp,'Final_quan']+a    
    data3.loc[data3['Sold to Customer Name'] ==comp,'cust_type'] = 'Quan_changer_small'

data3['leadtime_crit'] = False
for comp in G3:    
    b=random.choices(np.arange(100,501,100),k=np.sum(data3['Sold to Customer Name'] ==comp))        
    data3.loc[data3['Sold to Customer Name'] ==comp,'Quan_amt_changed'] = b    
    data3.loc[data3['Sold to Customer Name'] ==comp,'Final_quan'] = data3.loc[data3['Sold to Customer Name'] ==comp,'Final_quan']+b    
    data3.loc[data3['Sold to Customer Name'] ==comp,'leadtime_crit'] = True    
    data3.loc[data3['Sold to Customer Name'] ==comp,'cust_type'] = 'Quan_changer_large'

for comp in G4:    
    data3.loc[data3['Sold to Customer Name'] ==comp,'order_times_changed'] = random.choices(np.arange(1,4), k=np.sum(data3['Sold to Customer Name'] ==comp))
    data3.loc[data3['Sold to Customer Name'] ==comp,'new_lead_time'] = random.choices(np.arange(5, 8),k= np.sum(data3['Sold to Customer Name'] ==comp))
    data3.loc[data3['Sold to Customer Name'] ==comp,'leadtime_crit'] = True    
    data3.loc[data3['Sold to Customer Name'] ==comp,'cust_type'] = 'date_changer_critical'   

data3.loc[data3['new_lead_time'] < data3['ori_lead_time'],'leadtime_crit'] = True

label_to_num = {
    'Normal' : 0,
    'date_changer' : 1,
    'Quan_changer_small' : 2,
    'Quan_changer_large' : 3,
    'date_changer_critical' : 4,    
    }

data3['cust_type_num'] = data3['cust_type'].map(label_to_num)

#%%
data4 = data3[{
    'Payment Term_x', 
    'Destination Port_x', 
    # 'Contract Execution Date',
    'Customer Type_x', 
    'Plant_x', 
    'Sold to Customer Name', 
    'Incoterm_x',
    'Customer Industry_x', 
    'Price Type', 
    'City State',
    'Shipping Condition_y', 
    # 'BL Date', 
    # 'Actual Delivery Date',
    # 'Quantity (MT)', 
    'ori_lead_time', 
    'order_times_changed',
    'new_lead_time', 
    'Quan_amt_changed', 
    'Final_quan', 
    'leadtime_crit',
    # 'cust_type'
    }]


#%% Changing to dummy variable
column_neg = [
    'Final_quan', 
    'ori_lead_time', 
    'new_lead_time' , 
    'order_times_changed',
    'Quan_amt_changed',
    'leadtime_crit'
    ]
column_names = data4.columns

# Initialisation
column_dict = {}
total_column = 0

for column in column_names:    
    if column not in column_neg:
        # print(column)
        
        # 1) Get unique entries in every column
        column_dict.update({column:data4[column].unique()})
        print(column + ' : ' + str(len(data3[column].unique())))
        total_column += len(data4[column].unique())
        
        # 2) Converting Categorical data to dummy variables
        # pd.get_dummies(data[column])
        # 3) And concatenating dummy data to data2
        data4 = pd.concat([data4,pd.get_dummies(data3[column])], axis=1)
        data4.drop([column], axis=1, inplace = True)
print(f'Total number of new dummy variables : {total_column}')


#%% Get Data for trainig classification
X = data4
y = data3[{
       'cust_type_num'
       }]

#%% Split
from sklearn.model_selection import train_test_split 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1) # 70% training and 30% test
X_test=X_test.sort_index()
y_test=y_test.sort_index()

#%%

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from sklearn import metrics

# Create Decision Tree classifer object
clf = DecisionTreeClassifier(
    criterion = "gini", 
    random_state = 70, 
    max_depth=None, 
    min_samples_leaf=1
    )

# Train Decision Tree Classifer
clf.fit(X,y)

#Predict the response for test dataset
y_pred = clf.predict(X)

# Model Accuracy, how often is the classifier correct?
print("Accuracy:",metrics.accuracy_score(y, y_pred))

feature_cols = X.columns

#%% Plot Tree
from sklearn.tree import export_graphviz  

# 2 ways to visualise plot

# 1) Export the decision tree to a tree.dot file 
# Go to link below and paste the output of tree.dot file
# https://dreampuf.github.io/GraphvizOnline

# 2) At command prompt
# To see the plot and convert to image, type this:
# >> dot -Tpng test.dot -o test.png

export_graphviz(clf, 
                out_file='class_tree2_70.dot',  
                filled=True, 
                rounded=True,
                special_characters=True,
                feature_names = feature_cols,
                class_names=data3['cust_type'].unique()
                )

#%% Visualise Graph in Spyder
import graphviz
dot_data = export_graphviz(clf, 
                out_file=None,  
                filled=True, 
                rounded=True,
                special_characters=True,
                feature_names = feature_cols,
                class_names=list(label_to_num.keys())
                )

graph = graphviz.Source(dot_data)

graph
