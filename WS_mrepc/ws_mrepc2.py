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
urls = pd.read_excel('input.xlsx', sheet_name='Sheet1', usecols='A')

#%% Linkedin: Set Driver and open webpage
print('\nMREPC: Open URL...')
chrome_driver = r'C:\Users\User\Documents\ghub_acceval\smarttradzt-python-services\chromedriver.exe'

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
designation = []
e_mail = []
office_address = []
tel_no = []
fax_no = []
website = []
factory = []

# 2nd table
prod_descr = []
category_name = []
brand_name = []
prod_certn = []

count= 0
page = 1

driver = webdriver.Chrome(chrome_driver, options=options)

# url = 'http://www.myrubbercouncil.com/marketplace/public/rubberproduct.php?rubbertype=RMD'
# url = 'http://www.myrubbercouncil.com/marketplace/public/search_products.php?category=002&subcategory=0000' #2pages
# url ='http://www.myrubbercouncil.com/marketplace/public/search_products.php?category=167&subcategory=0000'
# url ='http://www.myrubbercouncil.com/marketplace/public/search_productscat.php?category=003&subcategory=0010' #3pages
# url ='http://www.myrubbercouncil.com/marketplace/public/search_products.php?category=003&subcategory=0000' # 9 pages
# url = 'http://www.myrubbercouncil.com/marketplace/public/search_products.php?category=002&subcategory=0000' #2pages
# url = 'http://www.myrubbercouncil.com/marketplace/public/search_products.php?category=167&subcategory=0000' # catherer 1 page

#%% : Scraping Products

comp_profile_urls = []
view_catalogue_urls = []
for url in urls.iloc[:,0]:
    print(url)
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    driver.get(url)
    
    WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'crumb.global')))
    
# =============================================================================
#     # Get Category name
# =============================================================================
    name = driver.find_element_by_class_name('crumb.global')
    cat_name = name.text.split(' > ')[-1].split(' | ')[0]
    
    if 'Search' in cat_name:
        cat_name = cat_name.split(" : ")[-1]
        
    print('\n' + cat_name)    
    
# =============================================================================
#   # Pagination
# =============================================================================
    list_page_top = driver.find_elements_by_class_name('listBatch.listPage')
    page = list_page_top[0].find_elements_by_class_name('page_count')
    # page[-1].get_attribute('href')
    
    print('Page 1')
    num_page = 0
# =============================================================================
#       # Gathering Company Profile and Catalogue URLs
# =============================================================================
    containers2 = driver.find_elements_by_class_name('itemBox.AD.nobox2')
    # comp_profile_urls = []
    # view_catalogue_urls = []
    
    for contnr in containers2:
        
        
        
        b = contnr.find_element_by_class_name('box6')
        c = b.find_element_by_tag_name('a')
        if c.text == 'Company Profile':
            # Category Name
            category_name.append(cat_name)
            comp_profile_urls.append(c.get_attribute('href'))
            
        elif c.text == 'View Catalogue':
            view_catalogue_urls.append(c.get_attribute('href'))

    if  page ==[] or page[0].text =='':
        pass

    else:
        num_page = int(page[-2].text)
        
        # Get list URLs
        url_list = []
        
        for i in range(0,num_page-1):
            print(f'Page {i+2}')
            list_page_top = driver.find_elements_by_class_name('listBatch.listPage')
            page = list_page_top[0].find_elements_by_class_name('page_count')
            url_new = page[-1].get_attribute('href')
            driver.get(url_new)
            
            containers2 = WebDriverWait(driver,7).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'itemBox.AD.nobox2')))
            
            # containers2 = driver.find_elements_by_class_name('itemBox.AD.nobox2')
    
            for contnr in containers2:
                
                
                b = contnr.find_element_by_class_name('box6')
                c = b.find_element_by_tag_name('a')
                if c.text == 'Company Profile':
                    # Category Name
                    category_name.append(cat_name)
                    comp_profile_urls.append(c.get_attribute('href'))
                elif c.text == 'View Catalogue':
                    view_catalogue_urls.append(c.get_attribute('href'))
    
    
    
#     if  page ==[] or page[0].text =='':
#         print('1 page')
#         num_page = 0    
    
# # =============================================================================
# #       # Gathering Company Profile and Catalogue URLs
# # =============================================================================
#         containers2 = driver.find_elements_by_class_name('itemBox.AD.nobox2')
#         comp_profile_urls = []
#         view_catalogue_urls = []
        
#         for contnr in containers2:
            
#             b = contnr.find_element_by_class_name('box6')
#             c = b.find_element_by_tag_name('a')
#             if c.text == 'Company Profile':
#                 comp_profile_urls.append(c.get_attribute('href'))
#             elif c.text == 'View Catalogue':
#                 view_catalogue_urls.append(c.get_attribute('href'))
        
#%% =============================================================================
#         # Scraping Company Profile urls
# =============================================================================
# url = 'http://www.myrubbercouncil.com/marketplace/public/company_details.php?mrepc_no=00980'
for url in comp_profile_urls:
    print('\n' + url)
    # url = comp_profile_urls[2]
    driver.get(url)
    
    count += 1
    print(f'Scraping Item {count}')
    
    # Company Name
    # category_name.append(cat_name)
    
    # Company Name
    comp_name = driver.find_element_by_class_name('refineTitle')
    companies.append(comp_name.text)
    
    # All Tables
    comp_prfl_ctnrs = driver.find_elements_by_class_name('refineBySearch.company_profile')
    
# =============================================================================
#   # First table
# =============================================================================
    a = comp_prfl_ctnrs[0]
    b = a.find_elements_by_tag_name('tr')
    b1 = [item.text.split(' : ')[0] for item in b[:7] if 'Factory :' not in item.text]
    
    # if len(b) > 7:
    #     b1.append(b[7].text.split(' :')[0])
    
    # c = b[0].text.split(' : ')
    
    if 'Contact Person' not in b1:
        contact_person.append('NA')
    
    if 'Designation' not in b1:
        designation.append('NA')
        
    if 'Email' not in b1:
        e_mail.append('NA')
    
    if 'Office Address' not in b1:
        office_address.append('NA')
    
    if 'Telephone No' not in b1:
        tel_no.append('NA')
        
    if 'Fax No' not in b1:
        fax_no.append('NA')

    if 'Website' not in b1:
        website.append('NA')
        
    # if 'Factory' not in b1:
    #     factory.append('NA')
    
    for i in range(0,len(b1)):
        # print(i)
        
        if b[i].text.split(' : ')[0] =='Contact Person':
            # Contact person
            if len(b[i].text.split(' : ')) > 1:
                contact_person.append(b[i].text.split(' : ')[1])
            else:
                contact_person.append('NA')
                
        if b[i].text.split(' : ')[0] =='Designation':
            # Contact person
            if len(b[i].text.split(' : ')) > 1:
                designation.append(b[i].text.split(' : ')[1])
            else:
                designation.append('NA')            
            
        if b[i].text.split(' : ')[0] == 'Email':
            # Contact person
            if len(b[i].text.split(' : ')) > 1:
                e_mail.append(b[i].text.split(' : ')[1])
            else:
                e_mail.append('NA')
                
        if b[i].text.split(' : ')[0] == 'Office Address':
            # Contact person
            if len(b[i].text.split(' : ')) > 1:
                office_address.append(b[i].text.split(' : ')[1])
            else:
                office_address.append('NA')
                
        if b[i].text.split(' : ')[0] == 'Telephone No':
            # Contact person
            if len(b[i].text.split(' : ')) > 1:
                tel_no.append(b[i].text.split(' : ')[1])
            else:
                tel_no.append('NA')
                
        if b[i].text.split(' : ')[0] == 'Fax No':
            # Contact person
            if len(b[i].text.split(' : ')) > 1:
                fax_no.append(b[i].text.split(' : ')[1])
            else:
                fax_no.append('NA')
                
        if b[i].text.split(' : ')[0] == 'Website':
            # Contact person
            if len(b[i].text.split(' : ')) > 1:
                website.append(b[i].text.split(' : ')[1])
            else:
                website.append('NA')
                
        if b[i].text.split(' :')[0] == 'Factory':
            # Contact person
            if len(b[i].text.split(' :')) > 1:
                factory.append(b[i].text.split(' :')[1].lstrip('\n'))
            else:
                factory.append('NA')
                
                
                
       
        # # Office Address
        # if len(b[3].text.split(' : ')) > 1:
        #     office_address.append(b[3].text.split(' : ')[1])
        # else:
        #     office_address.append('NA')
            
        # # Telephone Number
        # if len(b[4].text.split(' : ')) > 1:
        #     tel_no.append(b[4].text.split(' : ')[1])
        # else:
        #     tel_no.append('NA')
            
        # # Fax Number
        # if len(b[5].text.split(' : ')) > 1:
        #     fax_no.append(b[5].text.split(' : ')[1])
        # else:
        #     fax_no.append('NA')
            
        # # Website
        # if len(b[6].text.split(' : ')) > 1:
        #     website.append(b[6].text.split(' : ')[1])
        # else:
        #     website.append('NA')
            
        # # Factory
        # if len(b[7].text.split(' :')) > 1:
        #     factory.append(b[7].text.split(' :')[1].lstrip('\n'))
        # else:
        #     factory.append('NA')
        
# =============================================================================
#   # Second table
# =============================================================================
    c = comp_prfl_ctnrs[1]
    d = c.find_elements_by_tag_name('tr')
    e = [item.text.split(' : ')[0] for item in d]
    
    # if
    if 'Product Description' not in e:
        prod_descr.append('NA')
    
    if 'Brand Name' not in e:
        brand_name.append('NA')
        
    if 'Quality Certification' not in e:
        prod_certn.append('NA')
    
    # Product Description
    for i in range(0,len(d)):        
                        
        if d[i].text.split(' : ')[0] =='Product Description':                    
        
            if len(d[i].text.split(' : ')) > 1:
                prod_descr.append(d[i].text.split(' : ')[1])
            else:
                prod_descr.append('NA')
                
        elif d[i].text.split(' : ')[0] =='Brand Name':
            
            if len(d[i].text.split(' : ')) > 1:
                brand_name.append(d[i].text.split(' : ')[1])
            else:
                brand_name.append('NA')
        
        elif d[i].text.split(' : ')[0] =='Quality Certification':
            
            if len(d[i].text.split(' : ')) > 1:
                prod_certn.append(d[i].text.split(' : ')[1])
            else:
                prod_certn.append('NA')
    
# =============================================================================
#         # Scraping Catalogue URLs
# =============================================================================
# for url in view_catalogue_urls:
#     print(url)
#     # url = view_catalogue_urls[1]
#     driver.get(url)
    

    
    
#%% Compile and Prepare Data for export
df = pd.DataFrame(
    {
     'Product Category': category_name, 
     'Company':companies, 
     'Contact Person': contact_person, 
     'Designation' : designation, 
     'E-mail': e_mail,
     'Office Address': office_address,
     'Contact Number': tel_no, 
     'Fax': fax_no, 
     'Website': website,
     # 'Factory Address': factory,
     'Product Description': prod_descr,
     'Brand Name': brand_name,
     'Product Certification': prod_certn,
     }
    )


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


#%%



    
    
    
    
#     page = driver.find_elements_by_class_name('page_count')
    
#     if  page ==[] or page[0].text =='':
#         print('1 page')
#         num_page = 0
        
#         for item in containers:
#             count += 1
#             print(f'Item {count}')
            
#             category_name.append(cat_name)
#             companies.append(item.text.split('\n')[0])
            
#             # Contact person
#             if len(item.text.split('\n')[1].split(': ')) > 1:
#                 contact_person.append(item.text.split('\n')[1].split(': ')[1])
#             else:
#                 contact_person.append('NA')
            
#             # E-mail
#             if len(item.text.split('\n')[2].split(': ')) > 1:
#                 e_mail.append(item.text.split('\n')[2].split(': ')[1])
#             else:
#                 e_mail.append('NA')
                
#             # Contact Number
#             if len(item.text.split('\n')[3].split(': ')) > 1:
#                 contact_number.append(item.text.split('\n')[3].split(': ')[1])
#             else:
#                 contact_number.append('NA')
            
#             # fax
#             if len(item.text.split('\n')[4].split(': ')) > 1:
#                 fax.append(item.text.split('\n')[4].split(': ')[1])
#             else:
#                 fax.append('NA')
                        
#             # website
#             if len(item.text.split('\n')[5].split(': ')) > 1:
#                 website.append(item.text.split('\n')[5].split(': ')[1])
#             else:
#                 website.append('NA')
        
#     else:
#         print('More than 2 pages')        
        
#         for item in containers:
#             count += 1
#             print(f'Item {count}')
            
#             category_name.append(cat_name)
#             companies.append(item.text.split('\n')[0])
            
#             # Contact person
#             if len(item.text.split('\n')[1].split(': ')) > 1:
#                 contact_person.append(item.text.split('\n')[1].split(': ')[1])
#             else:
#                 contact_person.append('NA')
            
#             # E-mail
#             if len(item.text.split('\n')[2].split(': ')) > 1:
#                 e_mail.append(item.text.split('\n')[2].split(': ')[1])
#             else:
#                 e_mail.append('NA')
                
#             # Contact Number
#             if len(item.text.split('\n')[3].split(': ')) > 1:
#                 contact_number.append(item.text.split('\n')[3].split(': ')[1])
#             else:
#                 contact_number.append('NA')
            
#             # fax
#             if len(item.text.split('\n')[4].split(': ')) > 1:
#                 fax.append(item.text.split('\n')[4].split(': ')[1])
#             else:
#                 fax.append('NA')
                        
#             # website
#             if len(item.text.split('\n')[5].split(': ')) > 1:
#                 website.append(item.text.split('\n')[5].split(': ')[1])
#             else:
#                 website.append('NA')
                
#             # contact_person.append(item.text.split('\n')[1].split(': ')[1])
#             # e_mail.append(item.text.split('\n')[2].split(': ')[1])
#             # contact_number.append(item.text.split('\n')[3].split(': ')[1])
#             # fax.append(item.text.split('\n')[4].split(': ')[1])
        
#         num_page = int(page[-2].text)
        
#         # Pagination
#         for i in range(0,num_page-1):
#             print(i)
#             url_new = page[-1].get_attribute('href')
#             driver.get(url_new)
#             name = driver.find_element_by_class_name('crumb.global')
#             cat_name = name.text.split(' > ')[-1].split(' | ')[0]
            
#             if 'Search' in cat_name:
#                 cat_name = cat_name.split(" : ")[-1]
            
#             containers = driver.find_elements_by_class_name('box4')
#             page = driver.find_elements_by_class_name('page_count')
    
#             # Scraping items
#             for item in containers:
#                 count += 1
#                 print(f'Item {count}')
                
#                 category_name.append(cat_name)
#                 companies.append(item.text.split('\n')[0])
                
#                 # Contact person
#                 if len(item.text.split('\n')[1].split(': ')) > 1:
#                     contact_person.append(item.text.split('\n')[1].split(': ')[1])
#                 else:
#                     contact_person.append('NA')
                
#                 # E-mail
#                 if len(item.text.split('\n')[2].split(': ')) > 1:
#                     e_mail.append(item.text.split('\n')[2].split(': ')[1])
#                 else:
#                     e_mail.append('NA')
                    
#                 # Contact Number
#                 if len(item.text.split('\n')[3].split(': ')) > 1:
#                     contact_number.append(item.text.split('\n')[3].split(': ')[1])
#                 else:
#                     contact_number.append('NA')
                
#                 # fax
#                 if len(item.text.split('\n')[4].split(': ')) > 1:
#                     fax.append(item.text.split('\n')[4].split(': ')[1])
#                 else:
#                     fax.append('NA')
                
#                 # website
#                 if len(item.text.split('\n')[5].split(': ')) > 1:
#                     website.append(item.text.split('\n')[5].split(': ')[1])
#                 else:
#                     website.append('NA')
                
    
#     # for item in f:
#     #     count += 1
#     #     print(f'Item {count}')
        
#     #     category_name.append(cat_name)
#     #     companies.append(item.text.split('\n')[0])
#     #     contact_person.append(item.text.split('\n')[1].split(': ')[1])
#     #     e_mail.append(item.text.split('\n')[2].split(': ')[1])
#     #     contact_number.append(item.text.split('\n')[3].split(': ')[1])
#     #     fax.append(item.text.split('\n')[4].split(': ')[1])
#     #     website.append(item.text.split('\n')[5].split(': ')[1])
    
#     #%% Close website
# driver.close()


