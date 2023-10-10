import requests
from bs4 import BeautifulSoup

# Define the URL of the Realtor.ca search results page
url = "https://www.realtor.ca/map#ZoomLevel=12&Center=50.678114%2C-120.334330&LatitudeMax=50.73530&LongitudeMax=-120.17280&LatitudeMin=50.62086&LongitudeMin=-120.49586&Sort=6-D&PropertyTypeGroupID=1&TransactionTypeId=2&PropertySearchTypeId=1&Currency=CAD"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all property listings on the page
    property_listings = soup.find_all("div", class_="property-listing")

    # Loop through each property listing and extract information
    for listing in property_listings:
        
        
        # Extract house price
        price = listing.find("div", class_="listing-price").text.strip()

        # Extract number of bedrooms
        bedrooms = listing.find("div", class_="property-features").find("li", class_="property-feature-bedrooms").text.strip()

        # Extract square footage
        sqft = listing.find("div", class_="property-features").find("li", class_="property-feature-sqft").text.strip()
        
        
        # TODO Change to CSV saving
        # Print the extracted information
        print("Price:", price)
        print("Bedrooms:", bedrooms)
        print("Square Footage:", sqft)
        print("-" * 50)
else:
    print("Failed to retrieve the page. Status code:", response.status_code)
