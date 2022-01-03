import requests
import re
from bs4 import BeautifulSoup
import selenium
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome(PATH)


def Dell(link):
    list_of_prices = []
    list_of_links = []
    result = requests.get(link)
    print(result.status_code)
    print(result.headers)
    src = result.content
    soup = BeautifulSoup(src,'lxml')
    laptops = soup.find_all('article')

    for article_tag in laptops:
        price_class = article_tag.find("div", attrs = {'class': "ps-simplified-price-with-total-savings ps-hide-simplified-price-with-total-savings ps-price new-simplified-price-with-total-savings"})
        if price_class is not None:
            price = price_class.find("div", attrs = {'class':"ps-dell-price ps-simplified"})

            #Discounted prices have different html
            if(price_class.find("div",attrs = {'class':"ps-orig ps-simplified"})):
                span = price.find_all('span').pop()
                print(span.text)
                edited_string = span.text.replace(',','')

                #Get integer value
                CAD_value = float(re.search(r'(\d+\.\d+)', edited_string).group())
                list_of_prices.append(CAD_value)

                buy_button = article_tag.find("section", attrs = {'class':"ps-show-hide-bottom"})
                customize_and_buy = buy_button.find('a', attrs = {'class':"ps-btn ps-blue"})
                print(customize_and_buy.attrs['href'])
                list_of_links.append(customize_and_buy.attrs['href'])
            #No discounted price
            else:
                print(str(price.text.strip()))
                edited_string = price.text.strip().replace(',', '')
                CAD_value = float(re.search(r'(\d+\.\d+)', edited_string).group())
                list_of_prices.append(CAD_value)
                buy_button = article_tag.find("section", attrs = {'class': "ps-show-hide-bottom"})
                customize_and_buy = buy_button.find('a', attrs = {'class': "ps-btn ps-blue"})
                print(customize_and_buy.attrs['href'])
                list_of_links.append(customize_and_buy.attrs['href'])

    print(list_of_prices)
    print(list_of_links)
    dell_dict = dict(zip(list_of_prices, list_of_links))
    return dell_dict

def filter_dell_link(link,want_screen_size,filter_order,min,max):

    if(len(want_screen_size) > 0):
        link = link + '/' + want_screen_size[0] + "?appliedRefinements=15677,33791,15676,16854,15674,15672"
        temp_list_of_ignore_ids = []
        size_refinements = {"17-inch": "15677", "16-inch": "33791", "15-inch": "15676", "14-inch": "16854",
                            "13-inch": "15674", "11-inch": "15672"}

        for key in size_refinements:
            if key in want_screen_size:
                pass
            else:
                temp_list_of_ignore_ids.append(size_refinements[key])
        for i in temp_list_of_ignore_ids:
            if i in link:
                start_index = link.find(i)
                end_index = start_index + len(i)
                link = link.replace(i, "")
                link = link[:start_index] + link[start_index + 1:]
            if link[-1] == ',':
                link = link[:-1]

    if(filter_order != ""):
        sort_by_refinements = {"ascending": "price-ascending", "descending": "price-descending"}
        sort_by_refinements = {filter_order: sort_by_refinements[filter_order]}
        link = link + "&sortBy=" + next(iter(sort_by_refinements.values()))

    if((min != "") and (max != "")):
        price_range_refinements = {"min": min, "max": max}
        link = link + "&min=" + min + "&max=" + max

    return link

def HP_check_XPATH_exists(xpath1):
    try:
        driver.find_element(By.XPATH, xpath1)
    except NoSuchElementException:
        return False
    return True

def HP(link, user_screen_size_list,user_input):
    screen_size = [13,14,15,16,17]
    screen_size.sort()
    user_screen_size_list.sort()
    driver.get(link)
    filter_results = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/button").click()

    #filter screen sizes
    if(len(user_screen_size_list) > 0):
        index = 2
        for i in screen_size:
            if i not in user_screen_size_list:
                index += 1
                continue

            exists = HP_check_XPATH_exists("/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[4]/div/div[2]/ul/li[" + str(6) + "]/div/div/input")
            checkbox_link = ''
            if(exists == True):
                checkbox_link = "/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[4]/div/div[2]/ul/li[" + str(index) + "]/div/div/input"
            else:
                checkbox_link = "/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div/div[2]/ul/li[" + str(index) + "]/div/div/input"
            click_checkbox = driver.find_element(By.XPATH,checkbox_link)
            driver.execute_script("arguments[0].click();",click_checkbox)
            time.sleep(5)
            index += 1

    #Sort by ascending or descending

    if(user_input == 'descending'):
        value = '2'
        select = Select(driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[3]/div[1]/div[2]/div/div[1]/a/div/select'))
        select.select_by_index(value)
        time.sleep(2)
    elif(user_input == 'ascending'):
        value = '3'
        select = Select(driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[3]/div[1]/div[2]/div/div[1]/a/div/select'))
        select.select_by_index(value)
        time.sleep(2)



    #Price slider commented out because drag and drop by offest goes by pixels which i can't use because of different monitor size
    # elem1 = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div/div/div[2]/ul/li/div/div/span[1]')
    #         #'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[4]/div/div/div[2]/ul/li/div/div/span[1]'
    # elem2 = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div/div/div[2]/ul/li/div/div/span[2]')
    # ActionChains(driver).drag_and_drop_by_offset(elem1,60,0).perform()
    # time.sleep(2)
    # ActionChains(driver).drag_and_drop_by_offset(elem2,-60,0).perform()
    # time.sleep(2)

    #Create dict
    prices = []
    laptop_links = []
    parent_div = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div[3]/div[2]")
    count_of_divs = len(parent_div.find_elements_by_xpath("./div"))
    for laptop in range(1, count_of_divs+1):
        discount_string = HP_check_XPATH_exists('/html/body/div[4]/div/div/div/div[3]/div[2]/div[' + str(laptop) + ']/div[3]/div/div[1]/div/div/p[3]')
        if(discount_string == True):
            price = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[2]/div[' + str(laptop) +']/div[3]/div/div[1]/div/div/p[2]/nobr').get_attribute("innerHTML")
        else:
            price = driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[3]/div[2]/div[' + str(laptop) + ']/div[3]/div/div[1]/div/div/p[1]/nobr').get_attribute("innerHTML")
        print(price)
        prices.append(price)

        laptop_name = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[2]/div[' + str(laptop) + ']/div[2]/div[2]/h3/a').get_attribute('href')
        laptop_links.append(laptop_name)
        print(laptop_name)
        #'/html/body/div[4]/div/div/div/div[3]/div[2]/div[1]/div[3]/div/div[1]/div/div/p[1]/nobr'
                                              #product_list

    HP_dict = dict(zip(prices, laptop_links))
    return HP_dict


def Asus(link, want_screen_size,price,filter_order):
    available_screen_size = [12,13,14,15,16,17]
    driver.get(link)
    time.sleep(3)
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[6]/div[1]').click()
    time.sleep(1)
                                #'/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[6]/div[1]
                                #'/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[5]/div[1]
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[5]/div[1]').click()
    xpath_change = False
    if(len(want_screen_size) > 0):
        index = 1
        for i in available_screen_size:
            if i not in want_screen_size:
                index += 1
                continue
            time.sleep(2)

            if(xpath_change == False):
                checkbox_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[6]/div[2]/div[" + str(index) + "]/div/div[1]/input")
                                                                #'/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[6]/div[2]/div[2]/div/div[1]/input
                xpath_change = True
            else:
                checkbox_element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[1]/div[3]/div/div[6]/div[2]/div[" + str(index) + "]/div/div[1]/input" )
            if(checkbox_element.get_attribute("type") == "checkbox"):
                print("Is a checkbox")
            else:
                print("Not a checkbox")
            time.sleep(2)
            driver.execute_script("arguments[0].click();",checkbox_element)
            time.sleep(5)
            index += 1

    #Price required
    available_price = [499,500,1000,1500]
    if(len(price)>0):
        index = 1
        for i in available_price:
            if i not in price:
                index += 1
                continue
            if(xpath_change == False):
                checkbox_element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[5]/div[2]/div[" + str(index) + "]/div/div[1]/input")
                                                                #/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[5]/div[2]/div[2]/div/div[1]/input
                                                                #/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[1]/div[3]/div/div[5]/div[2]/div[2]/div/div[1]/input
                                                                #/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[1]/div[3]/div/div[5]/div[2]/div[3]/div/div[1]/input
                xpath_change = True
            else:
                checkbox_element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[1]/div[3]/div/div[5]/div[2]/div[" + str(index) + "]/div/div[1]/input")

            time.sleep(2)
            driver.execute_script("arguments[0].click();", checkbox_element)
            time.sleep(3)
            index += 1
    else:
        raise Exception("Asus website requires price filter")

def main():
    #Dell
    link = "https://www.dell.com/en-ca/shop/dell-laptops/sr/laptops"
    dell_filter = False
    if dell_filter is True:
        want_screen_size = ["17-inch","11-inch"]
        filter_order = "ascending"
        min = str(0)
        max = str(3000)
        link = filter_dell_link(link, want_screen_size, filter_order, min, max)

    #dell_dict = Dell(link)

    #HP
    user_screen_size_list = [14,16]
    link = 'https://www.hp.com/ca-en/shop/list.aspx?sel=NTB'
    user_input = 'descending' #'ascending' or 'descending' for result, otherwise you get no sorting
    #hp_dict = HP(link, user_screen_size_list,user_input)

    #Asus
    link = "https://www.asus.com/ca-en/Laptops/For-Home/All-series/"
    want_screen_size = [] #available screen sizes: 12,13,14,15,16,17
    price = [500] #You can only select one on Asus website: Available options are 499,500,1000,1500
    price.sort()
    filter_order = 'ascending'
    Asus_dict = Asus(link,want_screen_size,price,filter_order)


if __name__ == "__main__":
    main()