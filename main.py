# Library Imports
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import os

# List of request headers, extracted & filtered from chrome dev tools
HEADERS = {
    "method": "GET",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.5",
    "upgrade-insecure-requests": "1"
}

######################################################################################################################
# Description: Returns an array of strings with the required URLs to scrape, with all filters applied & 
#              with a parameter specifying the total number of pages that need to be traversed.  
# Parameters:
#   baseUrl -> string: Its the base URL with the filters applied, such as min & max budget, interior types etc.
#   pageCount -> int: Total number of pages you want the scraper to traverse and get the results from.
# Returns: An array of strings with the required URLs which can be directly called. 
######################################################################################################################
def UrlList(baseUrl: str, pageCount: int) -> list[str]:
    # Try fetching URL and return an empty array if the response is not successful
    try:
        print("Fetching URL: ", baseUrl)
        response = requests.get(baseUrl, headers=HEADERS)
        response.raise_for_status
    except:
        print("Error fetching URL: ", baseUrl)
        return []

    # Initializing my soup, nomnom
    siteHTML = BeautifulSoup(response.text, 'html.parser')

    # Get the inner string from 2nd last <li> element within a <ul> with class=pagination__list and convert it into an int
    maxPageCount = int(siteHTML.find_all("ul", class_="pagination__list")[0].find_all("li")[-2].a.string)

    if(pageCount > maxPageCount):
        print("There are only", maxPageCount, "pages of data available.")
        pageCount = maxPageCount # max number of pages to avoid duplicates

    urlList = []
    for i in range(pageCount):
        url = baseUrl + "/page-" + str(i+1)
        urlList.append(url)

    return urlList

######################################################################################################################
# Description: Fetches the HTML data from pararius.com with all the filters applied, page by page and parses
#              the different rental property listings and returns a 2D array with all the parsed info.
# Parameters:
#   city -> string: Name of the city where you want to search your rental properties in.
#   minPrice -> int: Minimum rental price for the properties you're interested in.
#   maxPrice -> int: Maximum rental price for the properties you're interested in.
#   interior -> string: The type of interior you want in your property i.e. Shell/Upholstered/Furnished
#   newPref  -> bool: The user preference if they only want new listings i.e. True if yes, otherwise False
# Returns: Returns a 2D array with all the parsed info in its appropriate format
######################################################################################################################
def fetchData(city="amsterdam", minPrice=0, maxPrice=60000,interior="", newPref=False):
    baseUrl = "https://www.pararius.com/apartments/" + city + "/" + str(minPrice) + "-" + str(maxPrice)
    
    if(len(interior) != 0):
        baseUrl += "/" + interior

    while(True):
        try:
            pageCount = int(input("How many webpages of data would you like to parse : "))
            break
        except:
            print("Enter a valid value!! Only integers allowed!")

    urlList = UrlList(baseUrl, pageCount)

    excelData = []
    for url in urlList:
        try:
            print("Fetching URL: ", url)
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status
        except:
            print("Error fetching URL: ", baseUrl)
            continue
        
        # Initializing my soup, nomnom
        responseHTML = BeautifulSoup(response.text, 'html.parser')
        listingsSection = responseHTML.find_all("li", class_="search-list__item search-list__item--listing")

        for listing in listingsSection:
            # Extracting listing's name
            listingName = (listing.section.h2.a.string).strip()

            # Extracting listing's status (New/Highlighted/Rented Under Options ...)
            listingLabelHTML = listing.section.find("div", class_="listing-search-item__label")
            listingStatus = ( (listingLabelHTML.span.string).strip() if listingLabelHTML != None else "")
            # If listing is not new and user is only interested in new listings then skip this listing!
            if("new" not in listingStatus.lower() and newPref):
                continue

            # Extracting listing's rent amount, removing commas, "per month" keyword and ??? sign to get just the number
            listingRentAmount = int((listing.section.find("div", class_="listing-search-item__price").string).strip().split("per")[0].split("???")[1].strip().replace(",",""))

            # Extracting listing's surface area, number of rooms and interior type
            listingFeatures = listing.section.find("div", class_="listing-search-item__features").ul.find_all("li")
            listingSurfaceArea = (listingFeatures[0].string).strip()
            listingNumberOfRooms = (listingFeatures[1].string).strip()
            listingInterior = (listingFeatures[2].string).strip()

            # Extracting listing's Pin Code and location
            listingLocation = (listing.section.find("div", class_="listing-search-item__sub-title").string).strip()

            # Extracting listing's pararius link
            listingLink = "https://www.pararius.com" + listing.section.h2.a["href"]

            # Extracting listing's estate agent details, name and agent link
            listingEstateAgent = listing.section.find("div", class_="listing-search-item__info").a
            listingEstateAgentName = (listingEstateAgent.string).strip()
            listingEstateAgentLink = "https://www.pararius.com" + listingEstateAgent["href"]

            listingData = [listingName, listingStatus, listingRentAmount, listingSurfaceArea, listingNumberOfRooms, listingInterior, listingLocation, listingLink, listingEstateAgentName, listingEstateAgentLink]
            excelData.append(listingData)

    if(len(urlList) >= 5):
        print("Phew! that was a lot of scraping. I'll need a coffee after this':)")

    return excelData

######################################################################################################################
# Description: Creates an outputs folder, if it doesn't exist and exports a 2D array into an excel file 
#              with proper naming convention via pandas.
# Parameters:
#   excelData -> List[List[]]: The 2D array which needs to be exported
# Returns: Nothing lol. Just exports the data into an excel file within outputs folder!
######################################################################################################################
def exportDataToExcel(excelData):
    # Extract current date and time
    currentDateTime = datetime.now()
    currentYear = str(currentDateTime.year)
    currentMonth = str(currentDateTime.month)
    currentDay = str(currentDateTime.day)
    currentHour = str(currentDateTime.hour)
    currentMinute = str(currentDateTime.minute)
    currentSecond = str(currentDateTime.second)

    # Create outputs directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)

    # Construct the filename and the excel sheet headers
    fileName = "Pararius_Scrape_" + currentDay + "-" + currentMonth + "-" + currentYear + "-" + currentHour+currentMinute+currentSecond+".xlsx"
    excelHeaders = ["Name", "Status", "Rent Amount (in EUR)","Surface Area", "Number of rooms", "Interiors", "Location", "Listing Link", "Estate Agent Name", "Estate Agent Link"]

    # Create pandas dataframe with export it with openpyxl engine, freezing the top row and removing indexes from rows.
    pdData = pd.DataFrame(excelData)
    pdData.to_excel(fileName, freeze_panes=(1, 0), engine="openpyxl", header=excelHeaders, index=False)
    
    # Move the generated excel sheet into the outputs folder
    os.replace(fileName, "./outputs/"+fileName)

# User input for the city and converting it into lowercase
print("Enter the city name where you want to search for rentals")
city = input().lower()

# Taking user input for minimum rental price and validating it
while(True):
    try:
        print("Enter the minimum rental price for the properties you're interested in (Leave blank and press enter if you have no preference)")
        minPrice = int(input())
        break
    except:
        print("Please enter a positive integer value!")

# Taking user input for maximum rental price and validating it
while(True):
    try:
        print("Enter the maximum rental price for the properties you're interested in (Leave blank and press enter if you have no preference)")
        maxPrice = int(input())
        break
    except:
        print("Please enter a positive integer value!")

# Taking user input for interior preference and validating it
while(True):
    try:
        print("Enter the type of interiors you're interested in")
        print("1 - Shell")
        print("2 - Upholstered")
        print("3 - Furnished")
        print("4 - No Perference!")
        interior = int(input("Enter your input: "))
        break
    except:
        print("Please enter a value from the above options or just press enter!")

# Taking user input if they want only new listings
while(True):
    try:
        print("Are you ONLY interested in new listing?")
        print("1 - Yes")
        print("2 - No")
        newPref = int(input("Enter your input: "))
        break
    except:
        print("Please enter a value from the above options only!")

# Mapping for user preference for new properties
newMapping = {
    1: True,
    2: False
}

# Mapping for interior options to their URL keywords
interiorMapping = {
    1: "shell",
    2: "upholstered",
    3: "furnished",
    4: ""
}

# Get all the required data
excelData = fetchData(city=city, minPrice=minPrice, maxPrice=maxPrice, interior=interiorMapping[interior], newPref=newMapping[newPref])

# Export the fetched data
exportDataToExcel(excelData)