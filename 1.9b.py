"""VR scrape, Steam 1.9a"""
#pylint: disable=locally-disabled, C0301, C0103, W0621, W0611, C0330, R0914, R0912, W0703
#Scrape all Steam filters (Relevance, Release Date, Name, Price, User Reviews)
#Grab all hrefs by xpath, de-dup, scrape error links via selenium

from datetime import datetime
import csv
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from lxml import html
import requests

csv.register_dialect('mydialect', delimiter='|', quotechar='"', doublequote=True, skipinitialspace=True, lineterminator='\r\n', quoting=csv.QUOTE_MINIMAL)

STEAM_URL = ['http://store.steampowered.com/search/?category1=998%2C994&vrsupport=401', #relevance
'http://store.steampowered.com/search/?sort_by=Released_DESC&category1=998%2C994&vrsupport=401', #release date, descending
'http://store.steampowered.com/search/?sort_by=Released_ASC&category1=998%2C994&vrsupport=401', #release date, ascending
'http://store.steampowered.com/search/?sort_by=Name_DESC&category1=998%2C994&vrsupport=401', #name, descending
'http://store.steampowered.com/search/?sort_by=Name_ASC&category1=998%2C994&vrsupport=401', #name, ascending
'http://store.steampowered.com/search/?sort_by=Price_DESC&category1=998%2C994&vrsupport=401', #highest price
'http://store.steampowered.com/search/?sort_by=Price_ASC&category1=998%2C994&vrsupport=401', #lowest price
'http://store.steampowered.com/search/?sort_by=Reviews_DESC&category1=998%2C994&vrsupport=401',#user reviews, descending
'http://store.steampowered.com/search/?sort_by=Reviews_ASC&category1=998%2C994&vrsupport=401',] #user reviews, ascending
#Links from filter parameters are scraped twice to minimize common Steam output errors

NONERROR = []
ERRORLINKS = []
FIXED = []
CSVOUTPUT = []

#helper functions ------- start
def is_int(string):
    """Checks if string is int"""
    try:
        int(string)
        return True
    except ValueError:
        return False

def is_date(string):
    """boolean check if string is m/d/Y"""
    try:
        datetime.strptime(string, '%b %d, %Y')#strips string into m/d/Y
        return True
    except ValueError:
        return False

def get_date(xpath):
    """Grabs release date and trims whitespace"""
    for child in xpath:#loops looking for child in array
        child = child.lstrip()#lstrips some data from child
        if is_date(child):
            return child

def get_headset_info(xpath):
    """Checks page for Oculus Rift or HTC Vive. Other HMDs need to be manually added to possmatch"""
    arr = []
    for possmatch in xpath:
        if possmatch == 'Oculus Rift' or possmatch == 'HTC Vive':
            if possmatch is not None:
                arr.append(possmatch)
    return arr

def de_dup(middleman):
    """Checks list of href collected in MIDDLEMAN for duplicates"""
    output = []
    seen = set()
    for link in middleman:
        print(link)
        if link == 'None':
            continue
        try:
            trunk = re.search('app/(.*?)/', link).group(1)
            if trunk not in seen:
                output.append(link)
                seen.add(trunk)
        except AttributeError:
            trunk = re.search('app/(.*?)/', link)
            if trunk not in seen:
                    output.append(link)
                    seen.add(trunk)
    return output

#helper functions ------- end

def get_filtered_links(steam_url):
    """Paginates & grabs all HREFs for all STEAM_URLs"""
    middleman = []
    for url in steam_url:
        page = requests.get(url)
        tree = html.fromstring(page.content)
        numofpages = tree.xpath('//div[@class="search_pagination_right"]/a/text()')
        lastpage = 1
        currentpage = 1

        for num in numofpages:
            if is_int(num):
                currint = int(num)
                if currint > lastpage:
                    lastpage = currint

        while currentpage <= lastpage:
            link_grab = tree.xpath('//*[@id="search_result_container"]/div[2]/a/@href')
            middleman = middleman + link_grab
            currentpage += 1
            page_int = requests.get('http://store.steampowered.com/search/?category1=998%2C994&vrsupport=401&page=' + str(currentpage))
            tree = html.fromstring(page_int.content)
            # print('(Looping..!)')
            #print(middleman)

        print('Oh, filter finished..!')

    return middleman

def get_app_info(game_links):
    """pulls game, genre, dev, pub, release, hmd, link data"""
    for link in game_links:
        try:
            appid = re.search('app/(.*?)/', link).group(1)
        except AttributeError:
            appid = re.search('app/(.*?)/', link)
        page = requests.get(link)
        tree = html.fromstring(page.content)
        # print(link)
        try:
            gamename = tree.xpath('//div[@class="details_block"]/text()')[1].lstrip()
        except IndexError:
            # print('Error, archived for Selenium scrape')
            ERRORLINKS.append([link])
            continue

        details_child = tree.xpath('//div[@class="details_block"]/*/text()')
        catget = ''

        genres = []
        developer = []
        publisher = []
        release_date = get_date(tree.xpath('//div[@class="details_block"]/text()'))
        if release_date is not None:
            release_date = release_date
        supported_hmd = get_headset_info(tree.xpath('//div[@class="game_area_details_specs"]/a[@class="name"]/text()'))
        try:
            price = tree.xpath('//div[@class="game_purchase_price price"]/text()')[0].strip()
        except IndexError:
            try:
                price = tree.xpath('//div[@class="discount_original_price"]/text()')[0].strip()
            except IndexError:
                price = ''

        for child in details_child:
            if child == 'Genre:':
                catget = 'Genre'
            if child == 'Developer:':
                catget = 'Developer'
            if child == 'Publisher:':
                catget = 'Publisher'
            if child == 'Release Date:':
                catget = ''
            if catget == 'Genre' and child != 'Genre:':
                if child is not None:
                    genres.append(child)
            if catget == 'Developer' and child != 'Developer:':
                if child is not None:
                    developer.append(child)
            if catget == 'Publisher' and child != 'Publisher:':
                if child is not None:
                    if '\n' not in child:
                        publisher.append(child)

        NONERROR.append([gamename, price, genres, developer, publisher, release_date, supported_hmd, link, appid])
        print(appid)

def selenium_get(errorlinks):
    """use selenium webdriver to manually bypass age-restriction"""
    driver = webdriver.Chrome()
    driver.get('http://store.steampowered.com/app/602130/Violent_killer_VR/')
    select = Select(driver.find_element_by_id("ageYear"))
    select.select_by_visible_text('1980')
    driver.find_element_by_xpath('//*[@id="agecheck_form"]/a/span').click()
    driver.get('http://store.steampowered.com/app/554920')
    driver.find_element_by_id("remember").click()
    driver.find_element_by_xpath('//*[@id="app_agegate"]/div[3]/a[1]').click()
    for url in errorlinks:
        driver.get(url)
        gamename = driver.find_element_by_class_name("apphub_AppName").text
        try:
            price = driver.find_element_by_css_selector("div.game_purchase_price.price").text
        except Exception:
            try:
                price = driver.find_element_by_xpath('//div[@class="discount_original_price"]').text
            except Exception:
                price = ''
        release_date = driver.find_element_by_class_name("date").text
        appid = re.search('app/(.*?)/', url).group(1)
        genres = []
        developer = []
        publisher = []
        catget = ''

        block = driver.find_element_by_class_name("block_content_inner")
        maybe = block.find_elements_by_xpath(".//*")
        for thing in maybe:
            if thing.text == 'Genre:':
                catget = 'Genre'
            if thing.text == 'Developer:':
                catget = 'Developer'
            if thing.text == 'Publisher:':
                catget = 'Publisher'
            if thing.text == 'Release Date:':
                break
            if catget == 'Genre' and thing.text != 'Genre:':
                if thing.text != '':
                    genres.append(thing.text)
            if catget == 'Developer' and thing.text != 'Developer:':
                if thing.text != '':
                    developer.append(thing.text)
            if catget == 'Publisher' and thing.text != 'Publisher:':
                if thing.text != '':
                    publisher.append(thing.text)

        all_HMD = driver.find_elements_by_class_name("game_area_details_specs")
        supported_hmd = []
        for headset in all_HMD:
            if headset.text == 'HTC Vive' or headset.text == 'Oculus Rift':
                supported_hmd.append(headset.text)

        FIXED.append([gamename, price, genres, developer, publisher, release_date, supported_hmd, url, appid])
        print(appid)

    driver.quit()

# ------- script run, get!
print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n    Part 1: LINK GET\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
middleman = get_filtered_links(STEAM_URL)

print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n      Part 2: DE-DUP\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
GAME_LINKS = de_dup(middleman)

print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n    Part 3: SCRAPE GO\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
get_app_info(GAME_LINKS)

'''print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n    Part 4: ERROR FIX\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
selenium_get(ERRORLINKS)''' #Error links can be grabbed but is not recommended due to Selenium package being prone to crashes.

print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n      Part 4: ERROR DUMP\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
name = datetime.today().strftime("%Y%m%d %H%M")
with open('Steam error %s.csv' % name, 'w', encoding='utf8') as mycsvfile:
    DATAWRITE = csv.writer(mycsvfile, dialect='mydialect')
    for row in ERRORLINKS:
        DATAWRITE.writerow(row)

print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n   Part 5: WRITING..!\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
CSVOUTPUT = NONERROR + FIXED

with open('Steam scrape %s.csv' % name, 'w', encoding='utf8') as mycsvfile:
    DATAWRITE = csv.writer(mycsvfile, dialect='mydialect')
    for row in CSVOUTPUT:
        DATAWRITE.writerow(row)

print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n        Job done.\n~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
