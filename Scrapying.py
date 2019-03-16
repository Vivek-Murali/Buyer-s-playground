#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 05:58:25 2019

@author: jetfire
"""

import urllib3 as ul 
from bs4 import BeautifulSoup
import os
import time
import requests
from urllib.request import urlopen
import random
import json
import pandas as pd
import os

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
hh = webdriver.ChromeOptions()
prefs = {"download.default_directory":"/Documents/Data/AG"} 
hh.add_experimental_option("prefs",prefs)
hh.add_argument("headless")
driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",chrome_options=hh)
#driver.set_window_size(1,10)
while True:
    link = 'http://agmarknet.gov.in/PriceAndArrivals/DatewiseCommodityReport.aspx'
    http = ul.PoolManager()
                                          
    page =http.request('GET',link)

    soup = BeautifulSoup(page.data)

    commodities = soup.find_all('select',id='middlepnl')


    driver.get(link) #opening the link in the driver .
    path1 = '//select[@id="cphBody_cboYear"]'
    year_element = driver.find_element_by_xpath(path1)
    year_select = Select(year_element)
    
    year_values =  [ '%s' % o.get_attribute('value') for o in year_select.options[1:] ]
    
    path2 = '//select[@id="cphBody_cboMonth"]'
    month_element = driver.find_element_by_xpath(path2)
    month_select = Select(month_element)
    
    month_values =  [ '%s' % o.get_attribute('value') for o in month_select.options[1:] ]
    def month_select_updated(driver):
        path2 = '//select[@id="cphBody_cboMonth"]'
        month_element = driver.find_element_by_xpath(path2)
        month_select = Select(month_element)
        try:
            month_select.text
        except StaleElementReferenceException:
            return True
        except:
            pass

        return False
        
        
        
    def get_state():
        path3 = '//select[@name="ctl00$cphBody$cboState"]'
        State_element = driver.find_element_by_xpath(path3)
        State_select = Select(State_element)
        return State_select

    def select_state():
        get_state()
        State_values =  [ '%s' % o.get_attribute('value') for o in State_select.options[1:] ]
        return State_values
    
    
    for value in year_values:
        year_select.select_by_value('2018')
        for x in month_values:
            month_select.select_by_value('January')
            wait = WebDriverWait(driver, 15)
            wait.until(ec.visibility_of_element_located((By.ID,"cphBody_cboState")))
            State_select = Select(driver.find_element_by_id('cphBody_cboState'))
            State_values =  [ '%s' % o.get_attribute('value') for o in State_select.options[1:] ]
            for y in State_values:
                State_select.select_by_value('Karnataka')
                wait = WebDriverWait(driver, 15)
                wait.until(ec.visibility_of_element_located((By.ID,"cphBody_cboCommodity")))
                Commodity_select = Select(driver.find_element_by_id('cphBody_cboCommodity'))
                Commodity_values =  [ '%s' % o.get_attribute('value') for o in Commodity_select.options[1:] ]
                for z in Commodity_values:
                    q = random.choice(Commodity_values)
                    Commodity_select.select_by_value('17')
                    wait = WebDriverWait(driver, 15)
                    wait.until(ec.visibility_of_element_located((By.NAME,"ctl00$cphBody$btnSubmit")))
                    driver.find_element_by_id("cphBody_btnSubmit").click()
                    wait = WebDriverWait(driver, 30)
                    wait.until(ec.visibility_of_element_located((By.NAME,"ctl00$cphBody$Button1")))
                    table = driver.find_elements(By.ID,"cphBody_gridRecords")
                    rows = driver.find_elements(By.TAG_NAME, "tr")
                    tb1 = driver.find_element_by_xpath('//*[@id="cphBody_gridRecords"]').get_attribute('outerHTML')
                    df= pd.read_html(tb1)
                    result = pd.concat([pd.DataFrame(df[i]) for i in range(len(df))],ignore_index=True)
                    #convert the pandas dataframe to JSON
                    result['Commodity_value'] = 17
                    result['State'] = "Karnataka"
                    json_records = result.to_json(orient='records')
                    #csv_records = result.to_csv("test.csv", index=False)
                    result.to_csv("test.csv", index=False)
                    print(json_records)
                    #os.system("mongoimport -d Checking -c test1 --type csv --file test.csv --headerline")
                    #print(json_records.items())
                    ##df2.to_csv("test.csv")
                    print("done")
                    #df['State'] = ["Karnataka"]
                    #df['Commodity_value'] = [17]
                    driver.close()        
                    '''wait = WebDriverWait(driver, 100)
                    wait.until(ec.visibility_of_element_located((By.ID,"cphBody_btnBack")))
                    driver.find_element_by_id("cphBody_btnBack").click()
                    '''
                
        
