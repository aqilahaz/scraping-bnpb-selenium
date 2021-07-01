
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
import pickle
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np


def clean_data(appended_data):
    print("Clean the data")
    #clean number in string in spesific column 
    #prov, kabkot, kecamatan, wilayah
    appended_data['desa']=appended_data['desa'].str.replace('\d+.(?![a-zA-Z])', '')
    appended_data['prov']=appended_data['prov'].str.replace('\d+.(?![a-zA-Z])', '')
    appended_data['kabkot']=appended_data['kabkot'].str.replace('\d+.(?![a-zA-Z])', '')
    appended_data['kecamatan']=appended_data['kecamatan'].str.replace('\d+.(?![a-zA-Z])', '')
    #delete row where None exist
    appended_data = appended_data.replace(to_replace='None', value=np.nan).dropna()
    #delete row where Total exist
    appended_data = appended_data.replace(to_replace='Total', value=np.nan).dropna()
    return appended_data

def parser(soup):
    #parsing the content of the table
    rows = []
    trs = soup.find_all('tr')
    headerow = [td.get_text(strip=True) for td in trs[2].find_all('th')] # header row
    if headerow: # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs: # for every table row
        rows.append([td.get_text(strip=True) for td in tr.find_all('td')])
    
    #get the column title
    ths=soup.find_all('th')[2:]
    kolom_a = ['desa']
    kolom_b = [th.text for th in ths]
    kolomm = kolom_a+kolom_b
    
    #convert to dataframe
    df = pd.DataFrame (rows, columns = kolomm)
    
    #add column 
    selected=soup.find_all('option', selected=True)
    df['prov'] = selected[1].text
    df['kabkot'] = selected[2].text
    df ['kecamatan'] = selected[3].text
    # data row
    return df

def get_value(options):
    value = []
    for element in options:
        val = element.get_attribute("value")
        value.append(val)  
    return value

def dropdown_awal(num):
    dropdown_a = driver.find_element_by_name("t")
    select_a = Select(dropdown_a)
    select_a.select_by_value(num)
    button_xpath = '/html/body/div/div[1]/section/div/div/div/div[1]/div[3]/form/div/a/small/i'
    button = driver.find_element_by_xpath(button_xpath)
    button.click()
    time.sleep(2)

def dropdown_kedua(val_b):
    dropdown_b = driver.find_element_by_name("p")
    select_b = Select(dropdown_b)
    select_b.select_by_visible_text(val_b)
    button_xpath = '/html/body/div/div[1]/section/div/div/div/div[1]/div[3]/form/div/a/small/i'
    button = driver.find_element_by_xpath(button_xpath)
    button.click()
    time.sleep(2)

def dropdown_ketiga(val_c, max_tries=5):
    dropdown_c = wait.until(EC.presence_of_element_located((By.NAME, 'k')))
    select_c = Select(dropdown_c)
    select_c.select_by_visible_text(val_c)
    time.sleep(2)

    button_xpath = '/html/body/div/div[1]/section/div/div/div/div[1]/div[3]/form/div/a/small/i'
    button = driver.find_element_by_xpath(button_xpath)
    button.click()
    time.sleep(2)
    
    
def dropdown_keempat(val_d, max_tries=5):

    dropdown_d = wait.until(EC.presence_of_element_located((By.NAME, 'c')))
    select_d = Select(dropdown_d)
    select_d.select_by_visible_text(val_d)
    button_xpath = '/html/body/div/div[1]/section/div/div/div/div[1]/div[3]/form/div/a/small/i'
    button = driver.find_element_by_xpath(button_xpath)
    button.click()
    time.sleep(2)

def take_dataframe(index):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        df=parser(soup)
        dataframe=clean_data(df)
        title = get_title(soup,index)
        write_to_csv(dataframe, title)
    except:
        pass

def write_to_csv(df,titles): 
    print("Write to CSV")
    df.to_csv(titles+".csv",index=False)
    print("Done")

def get_title(soup,index): 
    title=soup.find_all('h2')[0].text
    titles=title + " " + str(index)
    return titles

    
drv_path = "C:\\Users\\LENOVO\\Documents\\Magang\\scraping\\Facebook\\chromedriver\\chromedriver.exe"

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(drv_path, options=chrome_options)

url = 'http://bnpb.cloud/dibi/sp2010'
driver.get(url)
wait = WebDriverWait(driver, 20)
df=pd.read_excel("filee.xlsx")

for index, row in df.iterrows():
    try:
       
        dropdown_awal(str(row['tabel']))
        dropdown_kedua(row['prov'])
        dropdown_ketiga(row['kab'])
        dropdown_keempat(row['kec'])
        take_dataframe(index)
        time.sleep(2)
    except NoSuchElementException:
        dropdown_kedua(row['prov'])
        dropdown_ketiga(row['kab'])
        dropdown_keempat(row['kec'])
        take_dataframe(index)
        time.sleep(2)
    except TimeoutException as ex:
        print("Exception has been thrown. " + str(ex))
        time.sleep(60)
        print("Please wait 60 seconds")
        continue
    except KeyboardInterrupt:
        driver.quit()
    except:
        pass