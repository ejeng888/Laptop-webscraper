# Laptop-webscraper
Script that uses both Selenium and BeautifulSoup4 to search through Dell, HP, and Asus website to find laptops. Dell scraper function uses BeautifulSoup due to website simplicity. HP and Asus scraper functions use Selenium as they both contain a lot of javascript.

Within the config file, the user is allowed to filter by screen size, price, and whether you want the website to give you the most expensive or cheapest laptops given the price range.

After this, the script will do a comparison between all the laptops it found in each website and give you a CSV file of either the most expensive or the least expensive laptops between the three sites that match the user's specifications.

To run the program, ensure you have the Selenium, BeautifulSoup4, requests and configparser libraries. You will also need to have a Chrome Driver installed on your computer for Selenium to work. Paths can be edited in config file.


Known limitations and errors: 
  > For the Dell website, only 12 laptops can be obtained at a time. This will be fixed in the future.
  > When running the HP scraper function, pop-up ads may cause the program to hang. This can be resolved by simply closing the ad, which will resume to program.
