import time
from datetime import datetime
import re
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

CSVOUTPUT = []
LINKS = []
driver = webdriver.Firefox()
driver.get('https://www.linkedin.com/sales/search/companies')
email = driver.find_element_by_xpath('//*[@id="session_key-login"]')
pw = driver.find_element_by_xpath('//*[@id="session_password-login"]')

######################
email.send_keys('')###
######################
######################
pw.send_keys('')######
######################

driver.find_element_by_xpath('//*[@id="btn-primary"]').click()
time.sleep(3)

with open('auto_oem_get.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        LINKS.append(row[0])

for link in LINKS:
    dump = []

# search for company from previously loaded .csv
    driver.get('https://www.linkedin.com/sales/search/companies')
    time.sleep(5)
    find = driver.find_element_by_xpath('//*[@id="stream-container"]/div[1]/div[2]/section/div[3]/ul/li[1]/form/div/input')
    find.send_keys(link+'\ue007')
    time.sleep(2)
    thing = driver.find_elements_by_tag_name('a')

#grab the top 5 links
    _ = 0
    for item in thing:
        if _ == 5:
            break
        c = item.text
        f = str(item.get_attribute('href'))
        if re.search('sales/accounts', f) is not None:
            if c is not '':
                _ += 1
                dump.append([link, c, f.split("&")[0]])
    for index, dumpthing in enumerate(dump):
        driver.get(dumpthing[2])
        num = driver.find_element_by_class_name('empl-cnt').text
        dump[index].append(num)
    for entry in dump:
        print(entry)

    CSVOUTPUT = CSVOUTPUT + dump

csv.register_dialect('mydialect',delimiter='|',quotechar='"',doublequote=True,skipinitialspace=True,lineterminator='\r\n',quoting=csv.QUOTE_MINIMAL)

name = datetime.today().strftime("%Y%m%d %H%M")
with open('auto_oem_out %s.csv' %name, 'w', encoding='utf8') as mycsvfile:
    DATAWRITE = csv.writer(mycsvfile, dialect='mydialect')
    for row in CSVOUTPUT:
        DATAWRITE.writerow(row)
