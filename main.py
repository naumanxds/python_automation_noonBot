import csv
import time
import random

from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# constants used in code
NOT_FOUND = 'None'
BASE_URL = 'https://catalog.noon.partners'
ADMIN_NOON_CATALOG_URL = 'https://catalog.noon.partners/en-ae/catalog'

# create browser instance
browserOptions = Options()
browserOptions.add_argument("--headless")
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=browserOptions)

# login into Admin Panel
def loginAdmin():
    print(' => Loggin into the Admin Panel <=')
    userName = 'hamza.colorfultrading@gmail.com'
    userPassword = 'Attiq143$'
    try:
        driver.get(BASE_URL + '/en/')
        time.sleep(3)

        uName = driver.find_element_by_name('email')
        uPass = driver.find_element_by_name('password')    
        uName.clear()
        uPass.clear()
        uName.send_keys(userName)
        uPass.send_keys(userPassword)

        driver.find_element_by_xpath('//*[@id="formContainer"]/button').click()
        time.sleep(5)
        driver.get(ADMIN_NOON_CATALOG_URL)
        time.sleep(3)
        return driver

    except Exception as e:
        print('     >> ERRROR In Logging In => ' + format(e))

# Set Search criteria in the search bar
def setSearchCriteria(driver):
    print(' => Setting search Criteria for SKUs <=' )
    searchArray = ''
    with open('noon.csv', 'r') as fHandle:
        data = csv.reader(fHandle, delimiter=',')
        for l in data:
            searchArray += l[0] + ' '

    searchField = driver.find_element_by_class_name('searchInput')
    searchField.clear()

    searchField.send_keys(searchArray)
    time.sleep(3)

    return driver

# Extract all the links of the search criteria
def extractLinks(driver):
    print(' => Extracting Links Against Searched SKUs <=')
    links = []
    while True:
        driver.execute_script('return document.documentElement.outerHTML')
        html = BeautifulSoup(driver.page_source, 'lxml')
        tbody = html.find('tbody', {'class' : 'jsx-3498568516 tbody'})
        tr = tbody.find_all('tr')
        for l in tr:
            status = l.find('div', {'class' : 'jsx-448933760 statusCtr'}).get_text(strip=True)
            if str(status) == 'Live':
                links.append(l.find('a').get('href'))

        if str(html.find('li', {'class' : 'next'})) == NOT_FOUND or str(html.find('li', {'class' : 'next disabled'})) != NOT_FOUND:
            break

        driver.find_element_by_link_text('>>').click()
        time.sleep(3)

    return links, driver

# update prices for extracted links
def updateData(links, driver):
    print(' => Starting Updated of the Records <=')
    for l in links:
        driver.get(BASE_URL + l)
        time.sleep(3)
        html = BeautifulSoup(driver.page_source, 'lxml')
        lowestPriceSpan = html.find('div', {'class' : 'jsx-753764015 highLowPriceCtr'})
        lowestPrice = float(lowestPriceSpan.find_all('span')[-1].get_text(strip=True))

        myPriceField = html.find('div', {'class' : 'jsx-3185603393 priceInputWrapper'})
        myPrice = float(myPriceField.find('input').get('value'))

        if lowestPrice < myPrice:
            newPrice = str(round(lowestPrice - random.uniform(0.05, 0.25), 2))
            print('     => Updating Url : ' + BASE_URL + l)
            print('         => Lowest Price = ' + str(lowestPrice))
            print('         => My Price = ' + str(myPrice))
            print('         => Setting new Price = ' + newPrice)
            print('     ==============================================')
            setInput = driver.find_element_by_xpath('//*[@id="__next"]/div/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div[1]/div/div[1]/div[1]/div/div/input')
            setInput.clear()
            setInput.send_keys(newPrice)
            driver.find_element_by_class_name('primary').click()
            time.sleep(3)

    driver.quit()
    print(' => Execution Completet <=')

if __name__ == '__main__':
    print(' Starting Noon Bot ')
    print(' ================= ')
    links, driver = extractLinks(setSearchCriteria(loginAdmin()))
    updateData(links, driver)

