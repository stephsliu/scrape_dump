import time
import re
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def depart():
    try:
        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[2]/ul/li[1]/div/ul/li[1]/label').click()
    except Exception:
        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]/div/ul/li[1]/label').click()
    time.sleep(1)
    try:
        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[2]/ul/li[1]/div/ul/li[1]/button').click()
    except Exception:
        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]/div/ul/li[1]/button').click()
    time.sleep(1)
    return

companies = []
remainder = []
CSVOUTPUT = []

###
#companypage = 'https://www.linkedin.com/sales/accounts/insights?companyId='
###

csv.register_dialect('mydialect',delimiter='|',quotechar='"',doublequote=True,skipinitialspace=True,lineterminator='\r\n',quoting=csv.QUOTE_MINIMAL)

with open('LinkedIn_get.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        remainder.append(row[0])

with open('Linkedin_index.csv') as q:
    reader = csv.reader(q)
    for row in reader:
        companies.append(row[0])

driver = webdriver.Firefox()
prefix = 'https://www.linkedin.com/sales/search?facet=CC&facet.CC='
catget = ['Engineering', 'Arts and Design']
#catget = ['Quality Assurance']

#sign-in
driver.get('https://www.linkedin.com/sales/search/companies')
email = driver.find_element_by_xpath('//*[@id="session_key-login"]')
email.send_keys('utestacco@gmail.com')
pw = driver.find_element_by_xpath('//*[@id="session_password-login"]')
pw.send_keys('unitytest')
driver.find_element_by_xpath('//*[@id="btn-primary"]').click()

actions = ActionChains(driver)

time.sleep(3)

for companyID, companyName in zip(remainder, companies):
    driver.get(prefix+str(companyID))
    # for cat in catget:
    time.sleep(3)
    # companyname = driver.find_element_by_xpath('//*[@id="pivot-banner"]/div/div[1]/div/h1/a').text
    # print(companyname+' ('+companyID+')'+': '+employeecount)
    driver.find_element_by_class_name('view-all-filters').click()
    time.sleep(2)
    employeecount = driver.find_element_by_class_name('result-count').text
    #print(employeecount)
    block = driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section')
    # filtersearch = block.find_element_by_class_name('top-facets')
    filterblock = block.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]')
    time.sleep(3)
    try:
        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[2]/ul/li[1]/div/div[1]/span[1]').click()
    except Exception:
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[1]/ul/li[7]/div/div[1]/span[1]').click()
    #
    
    time.sleep(1)
    
    #filterthing = filterblock.find_element_by_xpath('//*[@id="FA-input"]')
    filterthing = driver.find_elements_by_class_name('add-values-container')
    

    i = 0
    for string in filterthing:
        if string.text == 'Add types of roles':
            for cat in catget:
                if i == 0:
                    string.send_keys(cat)
                    time.sleep(2)
                    string.send_keys('\ue007')
                    time.sleep(1)
                    #Engineering
                else:
                    depart()
                    #print('Category--',cat)
                    actions.send_keys(cat)
                    '''actions.perform()
                    actions.reset_actions()'''
                    time.sleep(1)
                    actions.send_keys('\ue007')
                    actions.perform()
                    time.sleep(1)
                    actions.reset_actions()
                    #the other ones, QA + arts and design
                    
                    #print(driver.find_element_by_xpath('//*[@id="pagekey-sales-search3-people"]/section/div[2]/div/p/div/section[2]/ul/li[1]/div/ul/li[1]/label/span').text)
                    '''if i == 2:
                        depart()
                        print('Departing..!')
                        actions.perform()'''
                    time.sleep(2)
                    
                    actions.reset_actions()
                    
                if i == 0:
                    engineering = driver.find_element_by_class_name('result-count').text
                    #print(cat+': '+engineering)
                    time.sleep(2)
                '''if i == 0:
                    qualityassurance = driver.find_element_by_class_name('result-count').text
                    #print(cat+': '+qualityassurance)
                    
                    time.sleep(2)'''
                if i == 1:
                    designers = driver.find_element_by_class_name('result-count').text
                    #print(cat+': '+designers)                       
                    time.sleep(2)
                i += 1
                if i >= 2:
                    break
            #print('Loop done.')
            break
    try:
        print(companyID, '|', employeecount, '|', engineering, '|', designers)
        CSVOUTPUT.append([companyID, employeecount, engineering, designers])
        #print(companyID, '|', employeecount, '|', qualityassurance)
        #CSVOUTPUT.append([companyID, employeecount, qualityassurance])
    except Exception:
        pass

with open('auto_oem_linkedin3.csv', 'w', encoding='utf8') as mycsvfile:
    DATAWRITE = csv.writer(mycsvfile, dialect='mydialect')
    for row in CSVOUTPUT:
        DATAWRITE.writerow(row)
