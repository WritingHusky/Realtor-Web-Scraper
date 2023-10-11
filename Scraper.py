import csv
import sys
import time
import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Define constants
URL = "https://www.realtor.ca/map#ZoomLevel=12&Center=50.678114%2C-120.334330&LatitudeMax=50.73530&LongitudeMax=-120.17280&LatitudeMin=50.62086&LongitudeMin=-120.49586&Sort=6-D&PropertyTypeGroupID=1&TransactionTypeId=2&PropertySearchTypeId=1&Currency=CAD"
WAIT_TIMEOUT = 30  # Adjust the timeout as needed
LOG_FILE = "scraper.log" 
DISCONNECTED_MSG = 'Unable to evaluate script: disconnected: not connected to DevTools\n'

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# Start a Selenium WebDriver session
driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox

# Navigate to the URL
driver.get(URL)
wait = WebDriverWait(driver, WAIT_TIMEOUT)

# Define used variables
scraped_data = []
running = True

# Give some time for the page to load and pass the "I am not a robot check"
# If you fail opps 
time.sleep(WAIT_TIMEOUT)
try:
    # Find the total number of pages
    page_count = driver.find_element(By.CLASS_NAME, "paginationTotalPagesNum").text.strip()

except Exception as e:
    logging.error(f"page count could not be found, The page might not have been loaded")
    driver.quit()
    sys.exit()

# Make the page count an int
if page_count.isdigit():
    page_count = int(page_count)
else:
    logging.error(f"Page Count retival failed {page_count} is not an int.")
    driver.quit()
    sys.exit()

 # Function to handle the end of a loop
def end():
    # Check there are still windows
    try:
        if len(driver.window_handles) != 0:
            # Close the new tab
            driver.close()
            # Switch back to the original tab (first tab)
            driver.switch_to.window(driver.window_handles[0])
        else:
            # End the program
            running = False
    except:
        if driver.get_log('driver')[-1]['message'] == DISCONNECTED_MSG:
            running = False

# Scrape the data from the linked lisitng        
def scrape_data():
    try:
        # Go to listing page and scrape the data needed
        action = webdriver.ActionChains(driver)
        action.context_click(link).key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()

        # Switch the new listing page
        driver.switch_to.window(driver.window_handles[1])

        # Let the page load
        wait.until(EC.presence_of_element_located((By.ID, "listingPriceValue")))
        
        # The set of data to scrape
        city_Str: str
        bedroom_Str: str
        bathroom_Str: str
        footage_Str: str

    
        # Scrape the data
        price_Str = driver.find_element(By.ID, "listingPriceValue").text.strip()
        city_Str = driver.find_element(By.XPATH, '//*[@id="listingAddress"]').text.strip()
        bedroom_Str = driver.find_element(By.XPATH, '//*[@id="BedroomIcon"]/'
                                            + '/div[@class="listingIconNum"]').text.strip()
        bathroom_Str = driver.find_element(By.XPATH, '//*[@id="BathroomIcon"]/'
                                            + '/div[@class="listingIconNum"]').text.strip()
        footage_Str = driver.find_element(By.XPATH, '//*[@id="propertyDetailsSectionContentSubCon_SquareFootage"]/'
                                            + '/div[@class="propertyDetailsSectionContentValue"]').text.strip()

        # Once the strings are made, format them into proper terms
        
        # Process the price of the listing
        price_Str = price_Str.replace('$', '')
        price_Str = price_Str.replace(',', '')
        if price_Str.isdigit():
            price = int(price_Str)
        else:
            print("price: " + price_Str + " is not a valid price")
            end()
            return
        
        # Get the city of the listing 
        city_index1 = city_Str.find("\n") + 1
        city_index2 = city_Str.find(',')
        city_Str = city_Str[city_index1:city_index2]

        # Process the number of bedrooms
        if bedroom_Str.isdigit():
            bedroom_int = int(bedroom_Str)
        else:
            print(bedroom_Str + " is not digits")
            end()
            return

        # Process the number of Bathrooms
        if bathroom_Str.isdigit():
            bathroom_int = int(bathroom_Str)
        else:
            print(bathroom_Str + " is not digits")
            end()
            return

        # Process the footage of the listing
        footage_index = footage_Str.find("sqft")
        footage_Str = footage_Str[:footage_index].strip()
        if footage_Str.isdigit():
            footage_int = int(footage_Str)
        else:
            print(footage_Str + " is not digits")
            end()
            return

        # Add fully scraped data to log later
        scraped_data.append([city_Str, price, bedroom_int, bathroom_int, footage_int])

        # Now everything is done go back to the main page
        end()

    # If the scraping fails go on to the next listing
    except Exception as e:
        if driver.get_log('driver')[-1]['message'] == DISCONNECTED_MSG:
            running = False
            return
        logging.error(f"listing failed: {e}")    
        end()
        return
    # end of scrape_data function

# Cycle through each page of listings
for page in range(page_count):
    try:
        # let the page load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listingDetailsLink")))
        # Parse through the small listings to get the links for the full listings
        listing_links = driver.find_elements(By.CLASS_NAME, "listingDetailsLink")
        
        if not listing_links:
            logging.warning(f"No listing links found on this page: {page}")
            break
        
        # Cycle through each listing on the page
        for i in range(len(listing_links)):

            # Find ith lisitng in the list
            listing_links = driver.find_elements(By.CLASS_NAME, "listingDetailsLink")
            link = listing_links[i]
            
            scrape_data() 
            
            # Stop running if there are no windows
            if not running:
                break       
    
        if not running:
            break

        # Click the next page button
        button = driver.find_element(By.CLASS_NAME, "lnkNextResultsPage")
        button.click()
        time.sleep(1)
    except NoSuchWindowException as e:
        logging.error(f"Window is not there: {e}")
        break
    except Exception as e:
        logging.error(f"An error occured: {e}")
        end()
        break
        
# End of the listing page loop

# Close the Selenium WebDriver session
try:
    driver.quit()
except Exception as e:
    logging.error(f"driver was already closed {e}")

# Write the data to a CSV file with unique name
with open('scraped_data ' + time.strftime("%A %d %b %Y %H-%M-%S") + '.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write the header row
    csv_writer.writerow(["City", "Price", "Bedrooms", "Bathrooms", "Square Footage"])
    # Write the data rows
    csv_writer.writerows(scraped_data)
    