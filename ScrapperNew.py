import sys
import time
from typing import KeysView
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Define the URL of the Realtor.ca search results page
url = "https://www.realtor.ca/map#ZoomLevel=12&Center=50.678114%2C-120.334330&LatitudeMax=50.73530&LongitudeMax=-120.17280&LatitudeMin=50.62086&LongitudeMin=-120.49586&Sort=6-D&PropertyTypeGroupID=1&TransactionTypeId=2&PropertySearchTypeId=1&Currency=CAD"

#print(url[:161])
#print(url[161:])
# 161 is the index start where the 

# Start a Selenium WebDriver session
driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox

# Navigate to the URL
driver.get(url)

# Give some time for the page to load and pass the "not a robot check"
# If you fail opps 
time.sleep(20)

# Get the page source after JavaScript content is loaded
page_source = driver.page_source

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(page_source, "html.parser")

# Find the total number of pages
page_count = soup.find(class_="paginationTotalPagesNum").text.strip()

# Print the total number of pages for testing
print("Total Pages:", page_count)
if page_count.isdigit():
    page_count = int(page_count)
else: 
    sys.exit()

# Parse through the small listings to get the links for the full listings

listing_Links = driver.find_elements(By.CLASS_NAME, "listingDetailsLink")

for link in listing_Links:
    
    # Go to listing page and scrape the data needed
    action = webdriver.ActionChains(driver)
    action.context_click(link).key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
    
    # Swtich the new listing page
    driver.switch_to.window(driver.window_handles[1])
    
    # Get the string of how much the listing is
    price_Str = driver.find_element(By.ID, "listingPriceValue").text.strip()
    
    # Process the string
    price_Str = price_Str.replace('$','')
    price_Str = price_Str.replace(',','')
    
    if price_Str.isdigit():
        price = int(price_Str)
    else: 
        price = 0
        
    city_Str: str
    bedroom_Str: str
    bathroom_Str: str
    footage_Str: str
    
    try:
        driver
    except:
        print("listing failed")
        continue

    

# simulate the scraping of data
time.sleep(10)


# Click the next page button
button = driver.find_element(By.CLASS_NAME, "lnkNextResultsPage")
button.click()

# Close the Selenium WebDriver session
driver.quit()