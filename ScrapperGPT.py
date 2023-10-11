import csv
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common import by, keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Define constants
URL = "https://www.realtor.ca/map#ZoomLevel=12&Center=50.678114%2C-120.334330&" \
    + "LatitudeMax=50.73530&LongitudeMax=-120.17280&LatitudeMin=50.62086&LongitudeMin=-120.49586&Sort=6-D&" \
    + "PropertyTypeGroupID=1&TransactionTypeId=2&PropertySearchTypeId=1&Currency=CAD"
WAIT_TIMEOUT = 10  # Adjust the timeout as needed
LOG_FILE = "scraper.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# Start a Selenium WebDriver session
driver = webdriver.Chrome()

# Navigate to the URL
driver.get(URL)
wait = WebDriverWait(driver, WAIT_TIMEOUT)

scraped_data = []

# Find the total number of pages
page_count = driver.find_element(by.By.CLASS_NAME, "paginationTotalPagesNum").text.strip()

# Print the total number of pages for testing
print("Total Pages:", page_count)
if page_count.isdigit():
    page_count = int(page_count)
else:
    sys.exit()

# Function to handle the end of a loop
def end():
    # Close the new tab
    if len(driver.window_handles) > 0:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    else:
        # End the program
        raise SystemExit

# Function to scrape data from a single listing
def scrape_listing(link):
    try:
        action = webdriver.ActionChains(driver)
        action.context_click(link).key_down(keys.Keys.CONTROL).click(link).key_up(keys.Keys.CONTROL).perform()
        driver.switch_to.window(driver.window_handles[1])

        # Wait for the listing page to load
        wait.until(EC.presence_of_element_located((by.By.ID, "listingPriceValue")))

        # Scrape data here
        city_Str = driver.find_element(by.By.XPATH, '//*[@id="listingAddress"]').text.strip()
        # ...

        # Add data to the list
        scraped_data.append([city_Str, price, bedroom_int, bathroom_int, footage_int])

        end()
    
    except Exception as e:
        logging.error(f"Listing failed: {str(e)}")
        end()

# Main scraping loop
for page in range(page_count):
    wait.until(EC.presence_of_element_located((by.By.CLASS_NAME, "listingDetailsLink")))
    listing_links = driver.find_elements(by.By.CLASS_NAME, "listingDetailsLink")
    
    for i, link in enumerate(listing_links):
        print(f"\nTrying listing: {i+1}")
        scrape_listing(link)
    
    try:
        button = driver.find_element(by.By.CLASS_NAME, "lnkNextResultsPage")
        button.click()
        wait.until(EC.presence_of_element_located((by.By.CLASS_NAME, "listingDetailsLink")))
    except Exception as e:
        logging.error(f"Failed to navigate to the next page: {str(e)}")
        break

# Write the data to a CSV file with a unique name
csv_file_name = 'scraped_data_' + time.strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
with open(csv_file_name, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write the header row
    csv_writer.writerow(["City", "Price", "Bedrooms", "Bathrooms", "Square Footage"])
    # Write the data rows
    csv_writer.writerows(scraped_data)

# Close the Selenium WebDriver session
driver.quit()
