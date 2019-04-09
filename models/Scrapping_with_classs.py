#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 17:08:50 2019

@author: jetfire
"""


'''chrome_options = Options()
chrome_options.binary_location = GOOGLE_CHROME_BIN
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)'''
#imports 
import pandas as pd
from common.database import Database
import json
import os
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


#class defination
class Check(object):
    
    @staticmethod
    def check(month,year,comm_val):
        chrome_options = ChromeOptions()
        chrome_options.binary_location = os.environ['GOOGLE_CHROME_BIN']
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(executable_path= os.environ['CHROMEDRIVER_PATH'], chrome_options=chrome_options)
        '''
        hh = webdriver.ChromeOptions()
        hh.add_argument("headless")
        driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",chrome_options=hh)'''
        link = 'http://agmarknet.gov.in/PriceAndArrivals/DatewiseCommodityReport.aspx'
        driver.get(link) #opening the link in the driver .
        path1 = '//select[@id="cphBody_cboYear"]'
        year_element = driver.find_element_by_xpath(path1)
        year_select = Select(year_element)
        year_values =  [ '%s' % o.get_attribute('value') for o in year_select.options[1:] ]
        path2 = '//select[@id="cphBody_cboMonth"]'
        month_element = driver.find_element_by_xpath(path2)
        month_select = Select(month_element)
        month_values =  [ '%s' % o.get_attribute('value') for o in month_select.options[1:] ]
        for value in year_values:
            year_select.select_by_value(year)
            for x in month_values:
                month_select.select_by_value(month)
                wait = WebDriverWait(driver, 15)
                wait.until(ec.visibility_of_element_located((By.ID,"cphBody_cboState")))
                State_select = Select(driver.find_element_by_id('cphBody_cboState'))
                State_values =  [ '%s' % o.get_attribute('value') for o in State_select.options[1:] ]
                for y in State_values:
                    State_select.select_by_value('Karnataka')
                    wait = WebDriverWait(driver, 15)
                    wait.until(ec.visibility_of_element_located((By.ID,"cphBody_cboCommodity")))
                    Commodity_select = Select(driver.find_element_by_id('cphBody_cboCommodity'))
                    Commodity_values =  [ '%s' % o.get_attribute('value') for o in          Commodity_select.options[1:] ]
                    for z in Commodity_values:
                        Commodity_select.select_by_value(comm_val)
                        wait = WebDriverWait(driver, 15)
                        wait.until(ec.visibility_of_element_located((By.NAME,"ctl00$cphBody$btnSubmit")))
                        driver.find_element_by_id("cphBody_btnSubmit").click()
                        wait = WebDriverWait(driver, 30)
                        wait.until(ec.visibility_of_element_located((By.NAME,"ctl00$cphBody$Button1")))
                        tb1 = driver.find_element_by_xpath('//*[@id="cphBody_gridRecords"]').get_attribute('outerHTML')
                        df= pd.read_html(tb1)
                        result = pd.concat([pd.DataFrame(df[i]) for i in range(len(df))],ignore_index=True)
                        #convert the pandas dataframe to JSON
                        result.rename(columns={'Minimum Price(Rs./Quintal)':'Minimum Price','Maximum Price(Rs./Quintal)':'Maximum Price','Modal Price(Rs./Quintal)':'Modal Price'},inplace=True)
                        result['Commodity_value'] = comm_val
                        result['State'] = "Karnataka"
                        json_records = result.to_json(orient='records')
                        #result.to_csv("test2.csv", index=False)
                        print(type(json_records))
                        data = json.loads(json_records)
                        print(data)
                        Database.insert_many('test_run',data)
                        #os.system("mongoimport -d Checking -c test1 --type csv --file test.csv --headerline")
                        print("done")
                        driver.close()
        return True              
        
