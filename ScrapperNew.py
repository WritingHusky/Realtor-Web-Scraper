import sys
import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

# Define the URL of the Realtor.ca search results page
url = "https://www.realtor.ca/map#ZoomLevel=12&Center=50.678114%2C-120.334330&LatitudeMax=50.73530&LongitudeMax=-120.17280&LatitudeMin=50.62086&LongitudeMin=-120.49586&Sort=6-D&PropertyTypeGroupID=1&TransactionTypeId=2&PropertySearchTypeId=1&Currency=CAD"

#print(url[:161])
# Start a Selenium WebDriver session
driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox

# Navigate to the URL
driver.get(url)

# Give some time for the page to load and pass the "not a robot check"
# If you fail opps 
time.sleep(30)

# Get the page source after JavaScript content is loaded
page_source = driver.page_source

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(page_source, "html.parser")

# Find the total number of pages
page_count = soup.find(class_="paginationTotalPagesNum").text.strip()

# Print the total number of pages
print("Total Pages:", page_count)

# Close the Selenium WebDriver session
driver.quit()

