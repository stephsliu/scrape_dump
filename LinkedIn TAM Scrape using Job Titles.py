########################################################################################################################
#WRITTEN BY: Stephen Phan
#UPDATED BY: Stephanie Liu
#UPDATED DATE: 12.7.2017  

#OBJECTIVE: Scrape LinkedIn employee, engineer+QA, and artist counts for calculating TAM.      
########################################################################################################################

import time
import re
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

#depart no longer functions as intended due to a change in the targetted pillbox
#def depart():
    #'''a function that closes the "Function" pill-box to allow something else to be inputted'''
    #try:
        #driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[2]/ul/li[1]/div/ul/li[1]/label').click()
    #except Exception:
        #driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]/div/ul/li[1]/label').click()
    #time.sleep(1)
    #try:
        #driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[2]/ul/li[1]/div/ul/li[1]/button').click()
    #except Exception:
        #driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]/div/ul/li[1]/button').click()
    #time.sleep(1)
    #return

########################################################################################################################
# CREATE DECLARATIONS        
########################################################################################################################

remainder = [] #companyIDs from .csv
CSVOUTPUT = [] #output
driver = webdriver.Firefox() #browser
actions = ActionChains(driver) #selenium queue
name = datetime.today().strftime("%Y%m%d %H%M") #for output name

prefix = 'https://www.linkedin.com/sales/search?facet=CC&facet.CC=' #prefix for URL

#create keyword inclusion and exclusions for search terms
engineeringcat = '(engineering OR engineer OR developer OR programmer OR qa OR quality assurance OR tester) AND NOT (artist OR animator OR animation OR designer OR 3d OR 2d OR producer OR graphic OR production OR creative OR lighting OR shading OR web OR back-end OR backend OR back end OR IT OR tools OR ambassador OR accounting OR reporting OR information OR incident OR localisation OR localization OR sales analytics OR salesforce OR analyst OR data OR systems OR system OR solutions OR solution OR campaign OR online OR security OR strategy OR operations OR hr OR network OR networking OR reliability OR infrastructure OR marketing)'
artistcat = '(artist OR animator OR animation OR designer OR 3d OR 2d OR producer OR graphic OR production OR creative OR lighting OR shading)'
catget = [engineeringcat, artistcat] #search terms

#.csv dialect
csv.register_dialect('mydialect',delimiter='|',quotechar='"',doublequote=True,
skipinitialspace=True,lineterminator='\r\n',quoting=csv.QUOTE_MINIMAL)

#open .csv with companyIDs
with open('Top30_Gaming_20171204.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        remainder.append(row[0])

########################################################################################################################     
# LOG INTO LINKEDIN SALES NAVIGATOR   
########################################################################################################################

#sign-in
driver.get('https://www.linkedin.com/sales/search/companies')
email = driver.find_element_by_xpath('//*[@id="session_key-login"]')
pw = driver.find_element_by_xpath('//*[@id="session_password-login"]')

# ACCOUNT 1 LOGIN CREDENTIALS
#email.send_keys('utestacco@gmail.com')
#pw.send_keys('unitytest')

# ACCOUNT 2LOGIN CREDENTIALS
email.send_keys('uttest0@gmail.com')
pw.send_keys('Utiny30!')

driver.find_element_by_xpath('//*[@id="btn-primary"]').click()

time.sleep(3)

########################################################################################################################       
#SCRAPING TEXT FROM APPROPRIATE PORTIONS OF UI USING XPATHS 
########################################################################################################################

#scrape get
for companyID in remainder:
    driver.get(prefix+str(companyID))
    time.sleep(3)
    driver.find_element_by_class_name('view-all-filters').click()
    time.sleep(2)
    employeecount = driver.find_element_by_class_name('result-count').text
    block = driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section')
    filterblock = block.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]')
    time.sleep(3)
    try: #clicks on the filter input box
        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[2]/ul/li[2]/div/div[1]/span[1]').click()
    except Exception:
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]/div/div[1]/span[1]').click()
    
    time.sleep(1)
    filterthing = driver.find_elements_by_class_name('add-values-container')

    i = 0
    for string in filterthing:
        if string.text == 'Job titles or boolean':
            for cat in catget:
                if i == 0: #searching first catget term
                    string.send_keys(cat)
                    time.sleep(2)
                    string.send_keys('\ue007')
                    time.sleep(1)
                else: #searching succeeding catget term(s)
                    
                    driver.get(prefix+str(companyID))
                    time.sleep(3)
                    driver.find_element_by_class_name('view-all-filters').click()
                    time.sleep(2)
                    employeecount = driver.find_element_by_class_name('result-count').text
                    block = driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section')
                    filterblock = block.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]')
                    time.sleep(3)
                    try:
                        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[2]/ul/li[2]/div/div[1]/span[1]').click()
                    except Exception:
                        time.sleep(1)
                        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]/div/div[1]/span[1]').click()
                    
                    time.sleep(1)
                    filterthing = driver.find_elements_by_class_name('add-values-container')                    
                    for string in filterthing:
                        if string.text == 'Job titles or boolean':
                            string.send_keys(cat)
                            time.sleep(2)
                            string.send_keys('\ue007')
                            time.sleep(1)
                            break
                    '''because depart did not work for the Title pill box, we are refreshing the page altogether as a patchwork work-around'''
                    #depart()
                    #actions.send_keys(cat)
                    #time.sleep(1)
                    #actions.send_keys('\ue007')
                    #actions.perform()
                    #time.sleep(1)
                    #actions.reset_actions()
                    #time.sleep(2)
                    #actions.reset_actions()
                if i == 0:
                    engineering = driver.find_element_by_class_name('result-count').text
                    time.sleep(2)
                if i == 1:
                    designers = driver.find_element_by_class_name('result-count').text                 
                    time.sleep(2)
                i += 1
                if i >= 2:
                    break
            break
    try:
        print(companyID, '|', employeecount, '|', engineering, '|', designers, sep='')
        CSVOUTPUT.append([companyID, employeecount, engineering, designers])
        #print(companyID, '|', employeecount, '|', qualityassurance)
        #CSVOUTPUT.append([companyID, employeecount, qualityassurance])
    except Exception:
        pass

########################################################################################################################  
# SAVE OUTPUT AS CSV      
########################################################################################################################

#writes CSVOUTPUT to .csv
with open('LinkedIn_out %s.csv' %name, 'w', encoding='utf8') as mycsvfile:
    DATAWRITE = csv.writer(mycsvfile, dialect='mydialect')
    for row in CSVOUTPUT:
        DATAWRITE.writerow(row)

########################################################################################################################
# END        
########################################################################################################################
