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
    
    def end():
         # Close the new tab
        driver.close()
        # Switch back to the original tab (first tab)
        driver.switch_to.window(driver.window_handles[0])
    
    # Go to listing page and scrape the data needed
    action = webdriver.ActionChains(driver)
    action.context_click(link).key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
    
    # Swtich the new listing page
    driver.switch_to.window(driver.window_handles[1])
    
    time.sleep(20)
    
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
        city_Str = driver.find_element(By.ID, "listingAddress").text.strip()
        #bedroom_Str = driver.find_element(By.ID, "BedroomIcon").find_element(By.CLASS_NAME, "listingIconNum ")
        bedroom_Str = driver.find_element(By.XPATH, '//*[@id="BedroomIcon"]/*[@class="listingIconNum]').text.strip()
        #bathroom_Str = driver.find_element(By.ID, "BathroomIcon").find_element(By.CLASS_NAME, "listingIconNum").text.strip()
        bathroom_Str = driver.find_element(By.XPATH, '//*[@id="BathroomIcon"]/*[@class="listingIconNum]').text.strip()
        #footage_Str = driver.find_element(By.ID, "propertyDetailsSectionContentSubCon_SquareFootage").find_element(By.CLASS_NAME,"propertyDetailsSectionContentValue")
        footage_Str = driver.find_element(By.XPATH, '//*[@id="propertyDetailsSectionContentSubCon_SquareFootage"]/*[@class="propertyDetailsSectionContentValue"]' ).text.strip()
        
        # Once the strings are made, format them into proper terms
        
        # Get the city of the listing 
        city_index = city_Str.find('>')
        city_Str = city_Str[city_index:]
        city_index = city_Str.find(',')
        city_Str = city_Str[:city_index]
        
        # Get the number of bedrooms
        if bedroom_Str.isdigit():
            bedroom_int = int(bedroom_Str)
        else: 
            print(bedroom_Str + " is not digits")
            end()
            continue
            
        # Get the number of bathrooms
        if bathroom_Str.isdigit():
            bathroom_int = int(bathroom_Str)
        else: 
            print(bathroom_Str + " is not digits")
            end()
            continue
        
        # Get the square footage of the listing
        footage_index = footage_Str.find("sqft")
        footage_Str = footage_Str[:footage_index]
        footage_Str = footage_Str.strip()
        
        if footage_Str.isdigit():
            footage_int = int(footage_Str)
        else:
            print(footage_Str + " is not digits")
            end()
            continue
    
    
    
    
    # If the scraping fails go on to the next listing
    except:
        print("listing failed")
        # Close the new tab
        driver.close()
        # Switch back to the original tab (first tab)
        driver.switch_to.window(driver.window_handles[0])
        continue


# Click the next page button
button = driver.find_element(By.CLASS_NAME, "lnkNextResultsPage")
button.click()

# Close the Selenium WebDriver session
driver.quit()