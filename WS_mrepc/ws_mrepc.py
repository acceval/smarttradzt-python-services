# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 15:22:39 2020

@author: James Ang
"""

#% Set Directory
import os, sys, subprocess
os.chdir(r'C:\Users\User\Documents\ghub_acceval\smarttradzt-python-services\WS_mrepc')

import re
import time
import pandas as pd
from datetime import datetime

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# import pkg_resources.py2_warn

from lib_scrape import append_df_to_excel

#%% Set URL
# url = 'http://www.myrubbercouncil.com/marketplace/public/rubberproduct.php?rubbertype=RMD'
# url = 'http://www.myrubbercouncil.com/marketplace/public/search_products.php?category=002&subcategory=0000' #2pages
# url ='http://www.myrubbercouncil.com/marketplace/public/search_products.php?category=167&subcategory=0000'
# url ='http://www.myrubbercouncil.com/marketplace/public/search_productscat.php?category=003&subcategory=0010' #3pages
url ='http://www.myrubbercouncil.com/marketplace/public/search_products.php?category=003&subcategory=0000' # 9 pages

urls = pd.read_excel('input.xlsx', sheet_name='Sheet1', usecols='A')

#%% Linkedin: Set Driver and open webpage
print('\nMREPC: Open URL...')
chrome_driver = r'C:\Users\User\Documents\ghub_acceval\smarttradzt-python-services\WS_mrepc\chromedriver.exe'

from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = False

if options.headless == True:
    print ("Headless Chrome Initialized on Linux")
    options.add_argument('--disable-gpu')
else:
    print ("Non-Headless")
    
# options.add_argument("--window-size=1920,1080");
options.add_argument("--start-maximized");

#%% Linkedin: Initialisation
companies = []
contact_person = []
e_mail = []
contact_number = []
fax = []
website = []
company_profile = []
category_name = []

count= 0
page = 1

driver = webdriver.Chrome(chrome_driver, options=options)

#%% : Scraping Products
for url in urls.iloc[:,0]:
    # print(url)
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    driver.get(url)
    
    # WebDriverWait(driver,5).until(
    #             EC.presence_of_all_elements_located((By.CLASS_NAME,'anchor')))
    
    
    name = driver.find_element_by_class_name('crumb.global')
    cat_name = name.text.split(' > ')[-1].split(' | ')[0]
    
    if 'Search' in cat_name:
        cat_name = cat_name.split(" : ")[-1]
        
    print('\n' + cat_name)
    f = driver.find_elements_by_class_name('box4')
    # g = f.find_elements_by_class_name("detail")
    
    page = driver.find_elements_by_class_name('page_count')
    
    if  page ==[] or page[0].text =='':
        print('1 page')
        num_page = 0               
        
        for item in f:
            count += 1
            print(f'Item {count}')
            
            category_name.append(cat_name)
            companies.append(item.text.split('\n')[0])
            
            # Contact person
            if len(item.text.split('\n')[1].split(': ')) > 1:
                contact_person.append(item.text.split('\n')[1].split(': ')[1])
            else:
                contact_person.append('NA')
            
            # E-mail
            if len(item.text.split('\n')[2].split(': ')) > 1:
                e_mail.append(item.text.split('\n')[2].split(': ')[1])
            else:
                e_mail.append('NA')
                
            # Contact Number
            if len(item.text.split('\n')[3].split(': ')) > 1:
                contact_number.append(item.text.split('\n')[3].split(': ')[1])
            else:
                contact_number.append('NA')
            
            # fax
            if len(item.text.split('\n')[4].split(': ')) > 1:
                fax.append(item.text.split('\n')[4].split(': ')[1])
            else:
                fax.append('NA')
                        
            # website
            if len(item.text.split('\n')[5].split(': ')) > 1:
                website.append(item.text.split('\n')[5].split(': ')[1])
            else:
                website.append('NA')
        
    else:
        print('More than 2 pages')        
        
        for item in f:
            count += 1
            print(f'Item {count}')
            
            category_name.append(cat_name)
            companies.append(item.text.split('\n')[0])
            
            # Contact person
            if len(item.text.split('\n')[1].split(': ')) > 1:
                contact_person.append(item.text.split('\n')[1].split(': ')[1])
            else:
                contact_person.append('NA')
            
            # E-mail
            if len(item.text.split('\n')[2].split(': ')) > 1:
                e_mail.append(item.text.split('\n')[2].split(': ')[1])
            else:
                e_mail.append('NA')
                
            # Contact Number
            if len(item.text.split('\n')[3].split(': ')) > 1:
                contact_number.append(item.text.split('\n')[3].split(': ')[1])
            else:
                contact_number.append('NA')
            
            # fax
            if len(item.text.split('\n')[4].split(': ')) > 1:
                fax.append(item.text.split('\n')[4].split(': ')[1])
            else:
                fax.append('NA')
                        
            # website
            if len(item.text.split('\n')[5].split(': ')) > 1:
                website.append(item.text.split('\n')[5].split(': ')[1])
            else:
                website.append('NA')
                
            # contact_person.append(item.text.split('\n')[1].split(': ')[1])
            # e_mail.append(item.text.split('\n')[2].split(': ')[1])
            # contact_number.append(item.text.split('\n')[3].split(': ')[1])
            # fax.append(item.text.split('\n')[4].split(': ')[1])
        
        num_page = int(page[-2].text)
        
        # Pagination
        for i in range(0,num_page-1):
            print(i)
            url_new = page[-1].get_attribute('href')
            driver.get(url_new)
            name = driver.find_element_by_class_name('crumb.global')
            cat_name = name.text.split(' > ')[-1].split(' | ')[0]
            
            if 'Search' in cat_name:
                cat_name = cat_name.split(" : ")[-1]
            
            f = driver.find_elements_by_class_name('box4')
            page = driver.find_elements_by_class_name('page_count')
    
            # Scraping items
            for item in f:
                count += 1
                print(f'Item {count}')
                
                category_name.append(cat_name)
                companies.append(item.text.split('\n')[0])
                
                # Contact person
                if len(item.text.split('\n')[1].split(': ')) > 1:
                    contact_person.append(item.text.split('\n')[1].split(': ')[1])
                else:
                    contact_person.append('NA')
                
                # E-mail
                if len(item.text.split('\n')[2].split(': ')) > 1:
                    e_mail.append(item.text.split('\n')[2].split(': ')[1])
                else:
                    e_mail.append('NA')
                    
                # Contact Number
                if len(item.text.split('\n')[3].split(': ')) > 1:
                    contact_number.append(item.text.split('\n')[3].split(': ')[1])
                else:
                    contact_number.append('NA')
                
                # fax
                if len(item.text.split('\n')[4].split(': ')) > 1:
                    fax.append(item.text.split('\n')[4].split(': ')[1])
                else:
                    fax.append('NA')
                
                # website
                if len(item.text.split('\n')[5].split(': ')) > 1:
                    website.append(item.text.split('\n')[5].split(': ')[1])
                else:
                    website.append('NA')
                
    
    # for item in f:
    #     count += 1
    #     print(f'Item {count}')
        
    #     category_name.append(cat_name)
    #     companies.append(item.text.split('\n')[0])
    #     contact_person.append(item.text.split('\n')[1].split(': ')[1])
    #     e_mail.append(item.text.split('\n')[2].split(': ')[1])
    #     contact_number.append(item.text.split('\n')[3].split(': ')[1])
    #     fax.append(item.text.split('\n')[4].split(': ')[1])
    #     website.append(item.text.split('\n')[5].split(': ')[1])
    
    #%% Close website
driver.close()

#%% Compile and Prepare Data for export
df = pd.DataFrame({'Product Category': category_name, 'Company':companies, 'Contact Person': contact_person, 'E-mail': e_mail, 'Contact Number':contact_number, 'Fax':fax, 'Website':website})

import openpyxl
# Create new workbook
wb = openpyxl.Workbook()

# Get SHEET name
# Sheet_name = wb.sheetnames

# Save created workbook at same path where .py file exist
filename = pd.read_excel('input.xlsx', sheet_name='Sheet1', usecols='E',nrows=1).iloc[0,0] +".xlsx"

wb.save(filename)
# dateTimeObj = datetime.now()
# timestampStr = dateTimeObj.strftime("%d%b%Y_%H%M%S")

# df.to_excel(filename+'.xlsx', index=False, encoding='utf-8')

# filename = r'C:/Users/User/Documents/ghub_acceval/smarttradzt-python-services/WS_mrepc/MREPC_.xlsx'
append_df_to_excel(filename, df)

