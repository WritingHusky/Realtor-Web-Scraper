import csv, sys, time
from selenium import webdriver
from selenium.webdriver.common import by, keys
from selenium.webdriver.support import expected_conditions as EC, ui

# Define the URL of the Realtor.ca search results page
url = "https://www.realtor.ca/map#ZoomLevel=12&Center=50.678114%2C-120.334330&"
+ "LatitudeMax=50.73530&LongitudeMax=-120.17280&LatitudeMin=50.62086&LongitudeMin=-120.49586&Sort=6-D&"
+ "PropertyTypeGroupID=1&TransactionTypeId=2&PropertySearchTypeId=1&Currency=CAD"

# Start a Selenium WebDriver session
driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox

# Navigate to the URL
driver.get(url)
wait = ui.WebDriverWait(driver, 20)

scraped_data = []
running = True

# Give some time for the page to load and pass the "not a robot check"
# If you fail opps 
time.sleep(20)

# Find the total number of pages
page_count = driver.find_element(by.By.CLASS_NAME, "paginationTotalPagesNum").text.strip()

# Print the total number of pages for testing
print("Total Pages:", page_count)
if page_count.isdigit():
    page_count = int(page_count)
else:
    sys.exit()

# Cycle through each page of listings
for page in range(page_count):

    # let the page load
    wait.until(EC.presence_of_element_located((by.By.CLASS_NAME, "listingDetailsLink")))
    # Parse through the small listings to get the links for the full listings
    listing_count = len(driver.find_elements(by.By.CLASS_NAME, "listingDetailsLink"))

    # Cycle through each listing on the page
    for i in range(listing_count):

        # Find ith lisitng in the list
        listing_links = driver.find_elements(by.By.CLASS_NAME, "listingDetailsLink")
        link = listing_links[i]

        # Function to handle the end of a loop
        def end():
            # Check there are still windows
            if len(driver.window_handles) is not 0:
                # Close the new tab
                driver.close()
                # Switch back to the original tab (first tab)
                driver.switch_to.window(driver.window_handles[0])
            else:
                # End the program
                running = False
                break 


        # Go to listing page and scrape the data needed
        action = webdriver.ActionChains(driver)
        action.context_click(link).key_down(keys.Keys.CONTROL).click(link).key_up(keys.Keys.CONTROL).perform()

        # Switch the new listing page
        driver.switch_to.window(driver.window_handles[1])

        # Let the page load
        wait.until(EC.presence_of_element_located((by.By.ID, "listingPriceValue")))

        # Get the price of the listing as a string
        price_Str = driver.find_element(by.By.ID, "listingPriceValue").text.strip()

        # Process the string
        price_Str = price_Str.replace('$', '')
        price_Str = price_Str.replace(',', '')

        # Make price an int
        if price_Str.isdigit():
            price = int(price_Str)
        else:
            print("price: " + price_Str + " is not a valid price")
            end()
            continue

        # The set of data to scrape
        city_Str: str
        bedroom_Str: str
        bathroom_Str: str
        footage_Str: str

        try:
            city_Str = driver.find_element(by.By.XPATH, '//*[@id="listingAddress"]').text.strip()
            
            bedroom_Str = driver.find_element(by.By.XPATH, '//*[@id="BedroomIcon"]/'
                                              + '/div[@class="listingIconNum"]').text.strip()

            bathroom_Str = driver.find_element(by.By.XPATH, '//*[@id="BathroomIcon"]/'
                                               + '/div[@class="listingIconNum"]').text.strip()
 
            footage_Str = driver.find_element(by.By.XPATH, '//*[@id="propertyDetailsSectionContentSubCon_SquareFootage"]/'
                                              + '/div[@class="propertyDetailsSectionContentValue"]').text.strip()

            # Once the strings are made, format them into proper terms
            
            # Get the city of the listing 
            city_index1 = city_Str.find("\n") + 1
            city_index2 = city_Str.find(',')
            city_Str = city_Str[city_index1:city_index2]
            print(city_Str)

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

            # Make footage an int
            if footage_Str.isdigit():
                footage_int = int(footage_Str)
            else:
                print(footage_Str + " is not digits")
                end()
                continue

            # Add fully scraped data to log later
            scraped_data.append([city_Str, price, bedroom_int, bathroom_int, footage_int])

            # Now everything is done go back to the main page
            end()

        # If the scraping fails go on to the next listing
        except Exception as e:
            print("listing failed" + str(e))
            # Close the new tab
            driver.close()
            # Switch back to the original tab (first tab)
            driver.switch_to.window(driver.window_handles[0])
            continue
    
    # Stop running if there are no windows
    if not running:
        break

    # Click the next page button
    button = driver.find_element(by.By.CLASS_NAME, "lnkNextResultsPage")
    button.click()
    time.sleep(1)

# Write the data to a CSV file with unique name
with open('scraped_data' + time.strftime("%A, %d %b %Y %H:%M:%S") + '.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write the header row
    csv_writer.writerow(["City", "Price", "Bedrooms", "Bathrooms", "Square Footage"])
    # Write the data rows
    csv_writer.writerows(scraped_data)

# Close the Selenium WebDriver session
driver.quit()
