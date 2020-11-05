#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 20:43:28 2020

@author: jamesv2
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# import pkg_resources.py2_warn

import pandas as pd
import os, sys, subprocess
import time
from datetime import datetime
import re
# import common_ws_lib

# from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())


#%% Set Directory
os.chdir('C:/Users/User/Documents/James/Webscrape/chemicals1/')

#%% Set URL
url = 'https://www.chemicals1.com/chemical-suppliers/asia'

#%% Linkedin: Set Driver and open webpage
print('\nChemicals1: Open URL...')
chrome_driver = 'C:/Users/User/Documents/James/Webscrape/chromedriver.exe'

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

#%% 
# driver = webdriver.Chrome(chrome_driver, options=options)
driver.get(url)

#%%
# ex_search = WebDriverWait(driver,10).until(
#                 EC.presence_of_element_located((By.CLASS_NAME,'builder-block.builder-c3fe009066f44de4af750ff4ad3477d9.css-1lqyowm')))

# ex_container = ex_search.find_elements_by_tag_name('a')
# x = 3
# item_name = ex_container[x].text
# ex_container[x].click()
# time.sleep(2)

# #%% Prepare for scrape
# driver.execute_script("window.scrollTo(0, 500);")
# driver.find_element_by_class_name('text-size.normal').click()
# # time.sleep(0.5)
# list_views = WebDriverWait(driver,5).until(
#                 EC.presence_of_all_elements_located((By.CLASS_NAME,'knowde-icons.ki-listview')))
# list_views[1].click()

#%% Linkedin: Initialisation
name = []
products_services = []
types = []
country = []
# info2 = []
address = []
companies = []
url =[]
count= 0
page = 1

#%% : Scraping Products

WebDriverWait(driver,5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME,'anchor')))

# got_it=WebDriverWait(driver,5).until(
#             EC.presence_of_element_located((By.CLASS_NAME,'cc-btn.cc-dismiss')))
# got_it.click()

f = driver.find_element_by_class_name('pagination')
g= f.find_elements_by_tag_name("li")

print('Chemicals1: Webscraping starts')

try:
    
    total_page = int(g[-2].text)
    
except Exception as e:
    
    print(e)
    total_page = 1
    
finally:
    
    while page <= int(total_page):
        print(page)
        articles = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'anchor')))

        for article in articles:
            count = count + 1
            ActionChains(driver).move_to_element(article).perform()
            # article = articles[0]
            """Name"""
            try:
                article.text.split('\n')[0]
                article.find_element_by_class_name('col-xs-6.col-md-4.col-sm-4.min-height150').text
                article.find_element_by_class_name('section-types.height17-overflowhidden').text
                article.find_element_by_class_name('section-services').text
                article.get_attribute('data-anchor')

            except NoSuchElementException:
                companies.append(article.text.split('\n')[0])
                address.append(article.find_element_by_class_name('col-xs-12.col-md-6').text)
                country.append(article.find_element_by_class_name('col-xs-12.col-md-6').text.split()[-1])
                print(article.find_element_by_class_name('col-xs-12.col-md-6').text.split()[-1])
                types.append(article.find_element_by_class_name('section-types.height17-overflowhidden').text)
                products_services.append(article.find_element_by_class_name('section-services').text)
                url.append(article.get_attribute('data-anchor'))
                print(f'Company {count}x')
                continue
            
            else:
                companies.append(article.text.split('\n')[0])
                address.append(article.find_element_by_class_name('col-xs-6.col-md-4.col-sm-4.min-height150').text)
                country.append(article.find_element_by_class_name('col-xs-6.col-md-4.col-sm-4.min-height150').text.split()[-1])
                print(article.find_element_by_class_name('col-xs-6.col-md-4.col-sm-4.min-height150').text.split()[-1])
                types.append(article.find_element_by_class_name('section-types.height17-overflowhidden').text)
                products_services.append(article.find_element_by_class_name('section-services').text)
                url.append(article.get_attribute('data-anchor'))

                print(f'Company {count}')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        f = driver.find_element_by_class_name('pagination')
        g= f.find_elements_by_tag_name("li")
        next_page = g[-1]
        next_page.click()
        
        page = page + 1

#%% Chemicals1: Close website
# driver.close()
# driver.switch_to.window(main_page)
# driver.close()
        
#%% Compile and Prepare Data for export
df = pd.DataFrame({'Company':companies, 'Address': address, 'Country': country, 'Types':types, 'Products/Services':products_services, 'url':url})#, 'Product Keyword': searched_keyword})
# df['email'] = 'found@noemail.com'

dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%d%b%Y_%H%M%S")
filename = 'Chemicals1_africa1' + timestampStr

df.to_excel(filename+'.xls', index=False, encoding='utf-8')
