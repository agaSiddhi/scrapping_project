import time
import numpy as np
import json

from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def get_url(company):
    COMPANY = company
    print('generating url')
    url = f'https://www.levels.fyi/companies/{COMPANY}/salaries/software-engineer?yoeChoice=junior&yacChoice=0&minYac=0&maxYac=0&sinceDate=0&offset=0&country=113&limit=50'
    return url


def get_salary(url):
    options = Options()
    service = Service('/usr/local/bin/chromedriver')
    options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.get(url)

    print('page loading')
    time.sleep(30)
    print('loading done')

    buttons = driver.find_elements(By.XPATH, '//*[@id="blur-prompt_blurPromptCell__qv6Ha"]/div/div/button')
    for button in buttons:
        if "Added Mine Already" in button.get_attribute('innerHTML'):
            button.click()
    
    time.sleep(2)

    buttons = driver.find_elements(By.XPATH, '//*[@id="blur-prompt_blurPromptCell__qv6Ha"]/div/div/button')
    for button in buttons:
        if "Remind Me Later" in button.get_attribute('innerHTML'):
            button.click()

    time.sleep(2)    

    div_buttons = driver.find_element(By.XPATH, '//*[@id="company-page_cardContainerId__MSgxF"]/div/div[1]/div/div[8]/table/tfoot/tr/td/div/div[2]/div')
    button_for_nxt_page = div_buttons.find_elements(By.TAG_NAME, 'button')

    if len(button_for_nxt_page)==1:
        num_of_page = 1
    else:
        num_of_page = int(button_for_nxt_page[-2].text)

    print(f"num_of_page: {num_of_page}")


    salaries = []
    for page in range(num_of_page-1):
        print(f"page: {page+1}")
        table = driver.find_element(By.XPATH, '//*[@id="company-page_cardContainerId__MSgxF"]/div/div[1]/div/div[8]/table')
        table = bs(table.get_attribute('innerHTML'), 'lxml')
        element = table.find_all('p', attrs={ 'class': 'MuiTypography-root MuiTypography-body1 css-1voc5jt'})
        time.sleep(1)

        take_next=False
        for idx, i in enumerate(element):
            if idx&1==0:
                year_of_exp=i.text[0]
                if year_of_exp  =='0':
                    take_next=True 
            if idx&1==1 and take_next:   
                salaries.append(i.text)
                take_next=False 

    # next button 
        button_for_nxt_page = driver.find_element(By.XPATH, '//*[@id="company-page_cardContainerId__MSgxF"]/div/div[1]/div/div[8]/table/tfoot/tr/td/div/div[2]/div').find_elements(By.TAG_NAME, 'button')
        page_next_button = button_for_nxt_page[-1]
        time.sleep(1)

        if page < num_of_page-1:
            page_next_button.click()

        time.sleep(5)

    driver.quit()
    return salaries


def salaries_str_to_int(salaries):
    salary_new = []
    for idx, salary in enumerate(salaries):
        salaries[idx] = salary.replace('US$', '').replace(',', '')
        salary_new.append(int(salaries[idx]))
    return salary_new


def to_json(salaries):
    median=np.median(np.array(salaries))
    return json.dumps({'median': median})



if __name__ == '__main__':
    company = input().lower()

    url = get_url(company)
    salaries=get_salary(url)
    salaries=salaries_str_to_int(salaries)
    median=to_json(salaries)
    
    print(median)  
    
      


