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
import csv
import os
import configparser
import ast

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.ini'))
PATH = config['directories']['chrome_driver_path']

def Dell_search(link):
    list_of_prices = []
    list_of_links = []
    result = requests.get(link)
    #print(result.status_code)
    #print(result.headers)
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
                edited_string = span.text.replace(',','')

                #Get integer value
                CAD_value = float(re.search(r'(\d+\.\d+)', edited_string).group())
                list_of_prices.append(CAD_value)

                buy_button = article_tag.find("section", attrs = {'class':"ps-show-hide-bottom"})
                customize_and_buy = buy_button.find('a', attrs = {'class':"ps-btn ps-blue"})
                list_of_links.append(customize_and_buy.attrs['href'])
            #No discounted price
            else:
                edited_string = price.text.strip().replace(',', '')
                CAD_value = float(re.search(r'(\d+\.\d+)', edited_string).group())
                list_of_prices.append(CAD_value)
                buy_button = article_tag.find("section", attrs = {'class': "ps-show-hide-bottom"})
                customize_and_buy = buy_button.find('a', attrs = {'class': "ps-btn ps-blue"})
                list_of_links.append(customize_and_buy.attrs['href'])

    print(list_of_prices)
    print(list_of_links)
    dell_dict = dict(zip(list_of_links,list_of_prices))
    return dell_dict

def filter_dell_link(link,want_screen_size,filter_order,min,max):
    #Screen size filter
    if(len(want_screen_size) > 0):
        link = link + '/' + str(want_screen_size[0]) + "?appliedRefinements=15677,33791,15676,16854,15674,15672"
        temp_list_of_ignore_ids = []
        size_refinements = {17: "15677", 16: "33791", 15: "15676", 14: "16854",
                            13: "15674", 11: "15672"}

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
    #Ascending or descending filter
    if(filter_order != ""):
        if(filter_order !="ascending" or filter_order != "descending"):
            print("No filter will be applied because improper value inputted")
            pass
        else:
            sort_by_refinements = {"ascending": "price-ascending", "descending": "price-descending"}
            sort_by_refinements = {filter_order: sort_by_refinements[filter_order]}
            link = link + "&sortBy=" + next(iter(sort_by_refinements.values()))
    #min and max filter
    if((min != "") and (max != "")):
        price_range_refinements = {"min": min, "max": max}
        link = link + "&min=" + min + "&max=" + max
    elif((min!="") and (max == "")):
        link = link + "&min=" + min
    elif((min=="") and (max != "")):
        link = link + "&max=" + max

    return link

def HP_check_XPATH_exists(driver,xpath1):
    #For some reason, the HP website layout changes randomnly. For example, when you reload the page, sometimes the first filter may either be "Usage" or it may be "Screen size."
    #Therefore, we check which version of website is currently being shown
    try:
        driver.find_element(By.XPATH, xpath1)
    except NoSuchElementException:
        return False
    return True

def HP_search(link, want_screen_size,filter_order,min,max):
    screen_size = [13,14,15,16,17]
    screen_size.sort()
    want_screen_size.sort()
    absolute_min = 379
    absolute_max = 4749
    if(min < absolute_min):
        raise Exception("The lowest possible price on HP website is 379. Change the min value")
    if(max > absolute_max):
        raise Exception("The highest possible price on HP website is 4749. Change the max value")
    driver = webdriver.Chrome(PATH)
    driver.get(link)
    filter_results = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/button").click()
    
    exists = HP_check_XPATH_exists(driver,"/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[3]/div/div[2]/ul/li[" + str(7) + "]/div/div/input")
    #Filter screen sizes
    if(len(want_screen_size) > 0):
        index = 2
        for i in screen_size:
            if i not in want_screen_size:
                index += 1
                continue
                                         
            checkbox_link = ''
            if(exists == True):
                #Screen size appears first instead of usage
                checkbox_link = "/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div/div[2]/ul/li[" + str(index) + "]/div/div/input"
                                 
            else: 
                #Usage appears first
                checkbox_link = "/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[3]/div/div[2]/ul/li[" + str(index) + "]/div/div/input"
            time.sleep(2)
            click_checkbox = driver.find_element(By.XPATH,checkbox_link)
            driver.execute_script("arguments[0].click();",click_checkbox)
            time.sleep(4)
            index += 1

    #Sort by ascending or descending
    if(filter_order == 'descending'):
        value = '2'
        select = Select(driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[3]/div[1]/div[2]/div/div[1]/a/div/select'))
        select.select_by_index(value)
        time.sleep(2)
    elif(filter_order == 'ascending'):
        value = '3'
        select = Select(driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[3]/div[1]/div[2]/div/div[1]/a/div/select'))
        select.select_by_index(value)
        time.sleep(2)
    else:
        print("No sorting will be applied because 'sort' is not valid. Only 'ascending' or 'descending' can be used.")
        print('\n')



    #Price slider, push slider to left and right in a loop via pixel. Stops once it reaches around the user given min and max
    if((min != "") and (max != "")):
        if(exists == True):

            slider_min = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[4]/div/div/div[1]/p/span[1]').get_attribute("innerHTML")
            while(int(slider_min) < min):   
                elem1 = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[4]/div/div/div[2]/ul/li/div/div/span[1]')
                ActionChains(driver).drag_and_drop_by_offset(elem1,20,0).perform()
                time.sleep(2)
                slider_min = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[4]/div/div/div[1]/p/span[1]').get_attribute("innerHTML")
            
            
            slider_max = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[4]/div/div/div[1]/p/span[2]').get_attribute("innerHTML")
            while(int(slider_max) > max):
                elem2 = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[4]/div/div/div[2]/ul/li/div/div/span[2]')
                ActionChains(driver).drag_and_drop_by_offset(elem2,-20,0).perform()
                time.sleep(2)
                slider_max = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[4]/div/div/div[1]/p/span[2]').get_attribute("innerHTML")
        
        else:
                                                
            slider_min = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div/div/div[1]/p/span[1]').get_attribute("innerHTML")                               #usage first
            while(int(slider_min) < min):   
                elem1 = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div/div/div[2]/ul/li/div/div/span[1]')
                ActionChains(driver).drag_and_drop_by_offset(elem1,20,0).perform()
                time.sleep(2)
                slider_min = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div/div/div[1]/p/span[1]').get_attribute("innerHTML")
                

            slider_max = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div/div/div[1]/p/span[2]').get_attribute("innerHTML")
            while(int(slider_max) > max):
                elem2 = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div/div/div[2]/ul/li/div/div/span[2]')
                ActionChains(driver).drag_and_drop_by_offset(elem2,-20,0).perform()
                time.sleep(2)
                slider_max = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/div/div/div[1]/p/span[2]').get_attribute("innerHTML")
               

    #Create dict
    prices = []
    laptop_links = []
    parent_div = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div[3]/div[2]")
    count_of_divs = len(parent_div.find_elements_by_xpath("./div"))
    for laptop in range(1, count_of_divs+1):
        discount_string = HP_check_XPATH_exists(driver,'/html/body/div[4]/div/div/div/div[3]/div[2]/div[' + str(laptop) + ']/div[3]/div/div[1]/div/div/p[3]')
        if(discount_string == True):
            price = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[2]/div[' + str(laptop) +']/div[3]/div/div[1]/div/div/p[2]/nobr').get_attribute("innerHTML")
        else:
            price = driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[3]/div[2]/div[' + str(laptop) + ']/div[3]/div/div[1]/div/div/p[1]/nobr').get_attribute("innerHTML")
        prices.append(price)

        laptop_name = driver.find_element(By.XPATH,'/html/body/div[4]/div/div/div/div[3]/div[2]/div[' + str(laptop) + ']/div[2]/div[2]/h3/a').get_attribute('href')
        laptop_links.append(laptop_name)

    #Convert prices to float
    for i in range(0,len(prices)):
        prices[i] = prices[i].strip()
        prices[i] = prices[i].replace('$','').replace(',','')
        prices[i] = float(prices[i])

    HP_dict = dict(zip(laptop_links,prices))
    driver.quit()
    time.sleep(2)
    return HP_dict

def Asus_search(link, want_screen_size,price,sort):
    #Find laptops on Asus website

    available_screen_size = [12,13,14,15,16,17]
    driver = webdriver.Chrome(PATH)
    driver.get(link)
    time.sleep(3)
    #Reveal screen size menu
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[6]/div[1]').click()
    time.sleep(1)
    #Reveal price menu
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[5]/div[1]').click()

    #Check if screen size is valid
    check =  all(item in available_screen_size for item in want_screen_size)
    if(check == True):
        pass
    else:
        raise Exception("Invalid screen size input. Only valid options are 12,13,14,15,16 and 17 for Asus website")

    #Select screen sizes
    xpath_change = False
    if(len(want_screen_size) > 0):
        index = 1
        for i in available_screen_size:
            if i not in want_screen_size:
                index += 1
                continue
            time.sleep(2)

            if(xpath_change == False):
                #For some reason, on Asus website the XPath changes after the first filter is applied. This if statement is to circumvent that
                checkbox_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[6]/div[2]/div[" + str(index) + "]/div/div[1]/input")                                   
                xpath_change = True
            else:
                checkbox_element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[1]/div[3]/div/div[6]/div[2]/div[" + str(index) + "]/div/div[1]/input" )
            time.sleep(2)
            driver.execute_script("arguments[0].click();",checkbox_element)
            time.sleep(5)
            index += 1

    
    available_price = [499,500,1000,1500]

    #Check if price is valid
    check =  all(item in available_price for item in price)
    if(check == True):
        pass
    else:
        raise Exception("Invalid price input. Only valid options are 499,500,1000, and 1500 for Asus website")

    #Select price range. Note: If selecting multiple screen sizes, you might not be able to select multiple prices. This is an issue with Asus website
    if(len(price)>0):
        index = 1
        for i in available_price:
            if i not in price:
                index += 1
                continue
            
            if(xpath_change == False):
                time.sleep(2)
                checkbox_element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div/div[5]/div[2]/div[" + str(index) + "]/div/div[1]/input")                                                         
                xpath_change = True
            else:
                time.sleep(3)
                checkbox_element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[1]/div[3]/div/div[5]/div[2]/div[" + str(index) + "]/div/div[1]/input")
                                                                #"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[1]/div[3]/div/div[5]/div[2]/div[2]/div/div[1]/input"
                                                                
            time.sleep(2)
            driver.execute_script("arguments[0].click();", checkbox_element)
            time.sleep(2)
            index += 1
    else:
        #Price required or Asus website won't give products. It will only give brands which isn't helpful
        raise Exception("Asus website requires price filter for specific laptops to be shown")

    #Sort by ascending or descending price. This can get you the most expensive or cheapest laptop
    if(sort != ""):
        drop_down_menu = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/div/div/div[1]/div")
        drop_down_menu.click()
        time.sleep(2)
        if(sort == 'ascending'):
            low_to_high = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[5]")
            driver.execute_script("arguments[0].click();", low_to_high)

        elif(sort == 'descending'):
            high_to_low = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[4]")
            driver.execute_script("arguments[0].click();",high_to_low)
        else:
            print("No sorting will be applied because 'sort' is not valid. Only 'ascending' or 'descending' can be used.")
            print('\n')
        time.sleep(2)

    product_links = []
    prices = []
    parent_div = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[2]")
    count_of_divs = len(parent_div.find_elements_by_xpath("./div"))
    #Get laptop links and prices
    for i in range(1, count_of_divs + 1):
        link = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[2]/div[" + str(i) + "]/div[7]/div[1]/a")
        price = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[2]/div[" + str(i) + "]/div[4]/div/div[2]/div")
        laptop_link = link.get_attribute("href")
        actual_price = price.get_attribute("innerHTML")
        product_links.append(laptop_link)
        prices.append(actual_price)

    #Convert prices list into list of float's
    prices2 = []
    for j in range(0,len(prices)):
        prices[j] = prices[j].strip().strip('\n')
        prices[j] = prices[j].replace('$','')
        prices[j] = prices[j].replace(',','')
        if(prices[j] != ''):
            prices2.append(prices[j])
    for k in product_links:
        if k == '':
            product_links.pop(k)
    prices = list(map(float,prices2))


    Asus_dict = dict(zip(product_links,prices))
    driver.quit()
    time.sleep(2)
    return Asus_dict

def main():

    list_of_dicts = []
    #Dell
    #Dell laptop searcher uses BeautifulSoup4 due to website simplicity
    link = "https://www.dell.com/en-ca/shop/dell-laptops/sr/laptops"
    dell_filter = config['Dell'].getboolean('Enable_filter')
    if dell_filter is True:
        want_screen_size = ast.literal_eval(config['Dell']['want_screen_size']) #Available screen sizes: 11,13,14,15,16,17
        filter_order = str(config['Dell']['filter_order']) #Available options are 'ascending' or 'descending'
        min = str(config['Dell']['min'])
        max = str(config['Dell']['max'])
        link = filter_dell_link(link, want_screen_size, filter_order, min, max)
        print("Dell link for verification is: ", link)
    dell_dict = Dell_search(link)
    print(dell_dict)
    list_of_dicts.append(dell_dict)
    print('\n')

    #HP
    #HP laptop searcher uses Selenium due to website complexity
    link = 'https://www.hp.com/ca-en/shop/list.aspx?sel=NTB'
    want_screen_size = ast.literal_eval(config['HP']['want_screen_size']) #Available screen sizes: 13,14,15,16,17
    filter_order = str(config['HP']['filter_order']) #Available options are 'ascending' or 'descending'
    min = int(config['HP']['min'])
    max = int(config['HP']['max'])
    Hp_dict = HP_search(link, want_screen_size,filter_order,min,max)
    print(Hp_dict)
    list_of_dicts.append(Hp_dict)
    print('\n')

    #Asus
    #Asus laptop searcher uses Selenium due to website complexity
    link = "https://www.asus.com/ca-en/Laptops/For-Home/All-series/"
    want_screen_size = ast.literal_eval(config['Asus']['want_screen_size']) #Available screen sizes: 12,13,14,15,16,17
    filter_order = str(config['Asus']['filter_order']) #Available options are 'ascending' or 'descending'
    price = ast.literal_eval(config['Asus']['price'])  #Available options are 499,500,1000,1500
    if((len(want_screen_size)>1) and (len(price)>1)):
        print("Warning: When more than one screen size and price is listed, the Asus website may prevent you from selecting more prices. As an example, on the Asus website, click filter by 13 and 14 inch screens, and then select a price. You will notice that you can't select more than one. This is a problem with Asus website and not one that can be controlled.")
        print("Therefore, it is recommended to only do one screen size at a time")
        print('\n','\n')
    Asus_dict = Asus_search(link,want_screen_size,price,filter_order)
    print(Asus_dict)
    list_of_dicts.append(Asus_dict)
    print('\n')


    #Find lowest or highest prices between the dictionaries
    lowest_or_highest_price = str(config['low_or_high']['lowest_or_highest_price'])
    complete_dictionary = {}
    print(lowest_or_highest_price)
    if(lowest_or_highest_price == "lowest"):
        index = 0
        for i in list_of_dicts:
            list_of_dicts[index] = dict(sorted(i.items(), key=lambda item: item[1]))
            print(list_of_dicts[index])
            for key,value in list_of_dicts[index].items():
                complete_dictionary[key] = value            
            index+=1
        complete_dictionary = dict(sorted(complete_dictionary.items(), key=lambda item: item[1]))
        
    elif(lowest_or_highest_price == "highest"):
        index = 0
        for i in list_of_dicts:
            list_of_dicts[index] = dict(sorted(i.items(), key=lambda item: item[1],reverse=True))
            print(list_of_dicts[index])
            for key,value in list_of_dicts[index].items():
                complete_dictionary[key] = value
            
            index+=1
        complete_dictionary = dict(sorted(complete_dictionary.items(), key=lambda item: item[1],reverse=True))
    else:
        raise Exception("Valid value not given for lowest_or_highest_price. Can only be 'lowest' or 'highest'.")
    print('\n',complete_dictionary)
        
    #Write to csv file
    save_path = config['directories']['save_path']
    filepath = r"{}".format(save_path)
    if os.path.exists(filepath):
        os.remove(filepath)
    with open(filepath, 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in complete_dictionary.items():
            writer.writerow([key, value])


if __name__ == "__main__":
    main()