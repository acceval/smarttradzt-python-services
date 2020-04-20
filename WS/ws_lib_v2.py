#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 14:24:55 2020

@author: alfred
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
# import pkg_resources.py2_warn

import pandas as pd
import os, sys, subprocess
import time
from datetime import datetime

from flask import Flask,request,jsonify,flash

chrome_driver = '/home/alfred/Documents/webscrape/chromedriver'
options = Options()
options.headless = False
if options.headless == True:
    print ("Headless Chrome Initialized on Linux")
    options.add_argument('--disable-gpu')
else:
    print ("Non-Headless")
    
options.add_argument("--window-size=1920,1080");
options.add_argument("--start-maximized");

#%% Initialisation
company_names = []
contact_person = []
designation = []

#%% India Plastic: Open webpage
def indplas(url1,searched_word):
    print('\nIndia PLastics: Open URL...')
    driver = webdriver.Chrome(chrome_driver, options=options)
    driver.get(url1)
    # driver.maximize_window(); 
    
    #%% India Plastic: Searched Word
    
    driver.find_element_by_xpath('//*[@name="keywords"]').send_keys(searched_word)
    driver.find_element_by_xpath('//*[@value="Go"]').click()
    
    #%% India Plastic: Scraping First page
    
    start_time = time.time()
    print('India PLastics: Webscraping starts...')
    company_container = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'homelink')))
    
    for i in range(0,len(company_container)):
        # print(i)
        company_names.append(company_container[i].text)
    
    #%% India Plastic: Scraping all pages
    try:
        page_container = WebDriverWait(driver,3).until(
                EC.presence_of_all_elements_located((By.XPATH,'//*[@id="AutoNumber3"]/tbody/tr[3]/td/center/table/tbody/tr/td/center/center/font/p/a')))
    
    except TimeoutException:
        pass
    else:    
        for pg in range(1,len(page_container)+1):
        
            # print(pg)
            driver.find_element_by_xpath(f'//*[@id="AutoNumber3"]/tbody/tr[3]/td/center/table/tbody/tr/td/center/center/font/p/a[{pg}]').click()
            company_container = WebDriverWait(driver,5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME,'homelink')))
           
            for i in range(0,len(company_container)):
                
                company_names.append(company_container[i].text)
        
        print(f'India PLastics: Webscraping completed. {len(company_names)} companies found.')
        print("India PLastics: Webscraping takes %s seconds ---" % round((time.time() - start_time),1))
    
    #%% India Plastic: Close website
    driver.close()
    print('India Plastic: URL closed')


# ALIBABA
def aliba(url2,searched_word):
    
#%% ALIBABA: Set Driver and open webpage
    print('\nAlibaba: Open URL...')
    driver = webdriver.Chrome(chrome_driver, options=options)
    driver.get(url2)
    driver.maximize_window(); 
    
    # # For Pop-up
    # WebDriverWait(driver,5).until(
    #             EC.presence_of_all_elements_located((By.CLASS_NAME,'double-close')))[0].click()
    
    #%% ALIBABA - Prepare for webscraping
    
    WebDriverWait(driver,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME,'ui-searchbar-keyword')))
    driver.find_element_by_class_name('ui-searchbar-keyword').clear()
    driver.find_element_by_class_name('ui-searchbar-keyword').send_keys(searched_word)
    time.sleep(3)
    WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'ui-searchbar-type-display')))[0].click()
    # a[0].click()
    sel_supp=WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'ui-searchbar-type-option')))#[0].click()
    
    print('Alibaba: Select Supplier, Trade and Verified...')
    sel_supp[1].click()
    
    driver.find_element_by_class_name('ui-searchbar-button-icon').click()
    
    trade_check = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.ID,'J-filter-ta')))
    trade_check.click()
    
    verified = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,'supplier-icon.icbu-certificate-icon.icbu-certificate-icon-verified')))
    verified.click()
    
    pagination = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,'ui2-pagination-show')))
    pagination_tag=pagination.find_elements_by_tag_name('a')
    pagination_tag[-1].click()
    
    #%% ALIBABA: Webscraping 
    count = 0
    page = 1
    
    start_time = time.time()
    print('Alibaba: Webscraping starts...')
    
    company_container = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'title.ellipsis')))
    
    f1 = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,'ui2-pagination-pages')))
    
    f = f1.find_elements_by_tag_name('a')
    
    total_page = int(f[-2].text)
    
    while page <= 2:#total_page: #2:
        try:
            print(f'Scraping page {page}')
            page = page + 1
            articles = WebDriverWait(driver,3).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME,'title.ellipsis')))
            
        except TimeoutException as e:
            print(e)
            continue
        else:
            for article in articles:
                ActionChains(driver).move_to_element(article).perform()          
                company_names.append(article.text)
                count = count + 1
                print(count)
       
            # print(count)
            next_page = WebDriverWait(driver,5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME,'next'))) #[0].click()
            ActionChains(driver).move_to_element(next_page[0]).click().perform()
        
    print(f'Alibaba: Webscraping completed. {count} companies found.')
    print("Alibaba: Webscraping takes %s seconds ---" % round((time.time() - start_time),1))
    
    #%% ALIBABA: Close website
    driver.close()
    print('Alibaba: URL closed')




#%% Linkedin: Set Driver and open webpage
def linkedin(url3,searched_word,job_fcn):
    
    print('\nLinkedin: Open URL...')
    driver = webdriver.Chrome(chrome_driver, options=options)
    driver.get(url3)
    # driver.maximize_window()
    # driver.set_window_size(1470, 1033)
    
    #%% Linkedin: Login
    
    print('Linkedin: Logging in...')
    idd = 'ck.chung@smarttradzt.com'
    pw = 'awesomeMe2020'
    
    WebDriverWait(driver,5).until(
                    EC.presence_of_element_located((By.ID,'username')))
    
    driver.find_element_by_id('username').clear()
    driver.find_element_by_id('username').send_keys(idd)
    driver.find_element_by_id('password').clear()
    driver.find_element_by_id('password').send_keys(pw)
    driver.find_element_by_class_name('btn__primary--large.from__button--floating').click()
    
    #%% Linkedin: Click sales Navigator
    print('Linkedin: Open Sales Navigator...')
    main_page = driver.window_handles[0]
    
    sales_navi = WebDriverWait(driver,5).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'global-nav__primary-item.global-nav__spotlight')))
    
    sales_navi.click()
    sales_navi_windows_handle = driver.window_handles[1]
    
    driver.switch_to.window(sales_navi_windows_handle)
    
    #%% Linkedin: Click Advanced Search
    print('Linkedin: Filling in Advanced search...')
    # adv_search = WebDriverWait(driver,5).until(
    #                 EC.presence_of_element_located((By.CLASS_NAME,'artdeco-dropdown__trigger.color-white.t-14.t-bold.artdeco-dropdown__trigger--non-button.flex.align-items-flex-end.artdeco-dropdown__trigger--placement-bottom.ember-view')))
    adv_search = WebDriverWait(driver,5).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'artdeco-dropdown.artdeco-dropdown--placement-bottom.artdeco-dropdown--justification-left.ember-view')))
    
    adv_search.click()
    time.sleep(0.2)
    leads = WebDriverWait(driver,5).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'artdeco-dropdown__item.artdeco-dropdown__item--is-dropdown.ember-view')))
    leads.click()
    # element = driver.find_element_by_id('ember51')
    
    
    # element.send_keys(Keys.TAB + Keys.ENTER)
    
    #%% Linkedin: Obtaining all filter handles
    
    filt_containers = WebDriverWait(driver,5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME,'flex.pt4.ph4.pb3.flex-wrap.cursor-pointer')))
    # custom_list = filt_containers[0]
    # custom_list = filt_containers[1]
    geography_handle = filt_containers[2]
    # custom_list = filt_containers[3]
    industry = filt_containers[4]
    # custom_list = filt_containers[5]
    # custom_list = filt_containers[6]
    # custom_list = filt_containers[7]
    # custom_list = filt_containers[8]
    senior_level_handle = filt_containers[9]
    function_handle = filt_containers[12]
    company_handle = filt_containers[15]
    
    #%% Linkedin: Filter by Geography
    
    def geo():
        
        geography_handle.click()
        
        geo_searched_region1 = 'Malaysia'
        geo_searched_region2 = 'Singapore'
        
        geo_enter = WebDriverWait(driver,5).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'text-input--no-border.mb4.ember-text-field.ember-view')))
        
        geo_enter.clear()
        
        geo_enter.send_keys(geo_searched_region1)
        time.sleep(1)
        geo1 = driver.find_elements_by_class_name("button--unstyled.link-without-visited-state.t-14.font-weight-400.cursor-pointer.search-filter-typeahead__suggestion-item-value.text-align-left")
        geo1[0].click()
        
        # Entering second location
        geo_enter.clear()
        geo_enter.send_keys(geo_searched_region2)
        time.sleep(0.5)
        geo1 = driver.find_elements_by_class_name("button--unstyled.link-without-visited-state.t-14.font-weight-400.cursor-pointer.search-filter-typeahead__suggestion-item-value.text-align-left")
        geo1[0].click()
        time.sleep(0.5)
    
    # geo()
        
    #%% Linkedin: Filter by seniority level
    print('Linkedin: Filter Seniority level')
    
    senior_level_handle.click()
    # senior_containers = WebDriverWait(driver,5).until(
    #                 EC.presence_of_all_elements_located((By.CLASS_NAME,'ph4.pb4.ember-view')))
    senior_containers = WebDriverWait(driver,5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME,'t-sans.flex.align-items-center.no-wrap')))
    
    for i in range(0,len(senior_containers)):
        print(i)
        if senior_containers[i].text == 
   
    
    snlev_enter = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'t-sans.flex.align-items-center ')))
    snlev_enter[4].find_element_by_tag_name('button').click()
    
    snlev_enter = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'t-sans.flex.align-items-center ')))
    snlev_enter[4].find_element_by_tag_name('button').click()
    
    snlev_enter = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'t-sans.flex.align-items-center ')))
    snlev_enter[4].find_element_by_tag_name('button').click()
    
    snlev_enter = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'t-sans.flex.align-items-center ')))
    snlev_enter[3].find_element_by_tag_name('button').click()
    
    #%% Linkedin: Filter by current company
    print('Linkedin: Filter Company')
    
    driver.find_element_by_class_name('advanced-search-filter__list').click()
    
    company_handle.click()
    
    company_enter = WebDriverWait(driver,5).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'text-input--no-border.ember-text-field.ember-view')))
    
    for company in company_names[0:15]:
        # print(company)
        company_enter.clear()
        company_enter.send_keys(company)
        company_enter.send_keys(Keys.ENTER)
    
    #%% Linkedin: Filter by function
    print('Linkedin: Filter Job function')
    
    # searched_function = input('Enter job function filter: ')
    searched_function = job_fcn
    
    function_handle.click()
    
    function_enter = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,'text-input--no-border.mb4.ember-text-field.ember-view')))
    
    function_enter.clear()
    
    function_enter.send_keys(searched_function)
    
    function_click = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,'button--unstyled.link-without-visited-state.t-14.font-weight-400.cursor-pointer.search-filter-typeahead__suggestion-item-value.text-align-left')))
    
    function_click.click()
    
    #%% Linkedin: Start search
    print('Linkedin: Start search for suspects')
    
    start_search = driver.find_element_by_class_name('button-primary-medium')
    start_search.click()
    driver.set_window_size(1657, 923) #just to load all data
    time.sleep(2)
    
    #%% Linkedin: Initialisation
    name = []
    position = []
    company = []
    location = []
    searched_keyword = []
    email = []
    found_email = "found@noemail.com"
    page = 1
    
    #%% Linkedin: Scraping prospects
    prospect_container = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME,'pv5.ph2.search-results__result-item')))
    
    f = driver.find_element_by_class_name('search-results__pagination-list').find_elements_by_tag_name('li')
    
    print('Linkedin: Webscraping starts')
    count= 0
    try:
        
        total_page = int(f[-1].find_element_by_tag_name('button').text)
        
    except Exception as e:
        
        print(e)
        total_page = 1
        
    finally:
        
        while page <= total_page:
            
            articles = WebDriverWait(driver,5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME,'pv5.ph2.search-results__result-item')))
    
            for article in articles:
                count = count + 1
                ActionChains(driver).move_to_element(article).perform()
                
                """Name"""
                try:
                    
                    article.find_element_by_class_name('result-lockup__name')               # Name
                    article.find_element_by_class_name('result-lockup__highlight-keyword')  # Position
                    article.find_element_by_class_name('result-lockup__misc-item')          # Location
                    article.find_element_by_class_name('result-lockup__position-company')   # Company
                
                except NoSuchElementException:
                    # print('var not defined')
                    # name.append("NA")
                    # position.append("NA")
                    # location.append("NA")
                    # company.append("NA")
                    continue
                
                else:
                    name.append(article.find_element_by_class_name('result-lockup__name').text)
                    position.append(article.find_element_by_class_name('result-lockup__highlight-keyword').find_element_by_class_name('t-14.t-bold').text)
                    location.append(article.find_element_by_class_name('result-lockup__misc-item').text)
                    company.append(article.find_element_by_class_name('result-lockup__position-company').find_element_by_tag_name('span').text)
                    searched_keyword.append(searched_word)
                    email.append(found_email)
                    print(f'Suspect {count}')          
               
            next_page = driver.find_element_by_class_name('search-results__pagination-next-button')
            next_page.find_element_by_class_name('v-align-middle').click()
            page = page + 1
    
    #%% Linkedin: Close website
    driver.close()
    driver.switch_to.window(main_page)
    driver.close()
    
    return name,position,location,company,searched_keyword,email