# Library Imports
from bs4 import BeautifulSoup
import requests
import pandas as pd

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

##################################################################################################################################################
# Description: Returns an array of strings with the required URLs to scrape, with all filters applied & 
#              with a parameter specifying the total number of pages that need to be traversed.  
# Parameters: 
#   baseUrl -> string: Its the base URL with all the filters applied, such as min and max budget, interior types and so on
#   pageCount -> int: Total number of pages you want the scraper to traverse and get the results from.
# Returns: An array of strings with the required URLs which can be directly called. 
##################################################################################################################################################
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
        print("There are only", maxPageCount, "pages available.")
        pageCount = maxPageCount # max number of pages to avoid duplicates

    urlList = []
    for i in range(pageCount):
        url = baseUrl + "/page-" + str(i+1)
        urlList.append(url)

    return urlList

"""
Example URLs
https://www.pararius.com/apartments/{City=Amsterdam}/{minPrice=0}-{maxPrice=60000}/{shell/upholstered/furnished}/page-4
https://www.pararius.com/apartments/{City=Amsterdam}/{minPrice=0}-{maxPrice=60000}/1-bedrooms/{shell/upholstered/furnished}/{25m2/50m2/75m2/100m2/125m2/150m2/200m2}/page-2
"""

def fetchData(city="amsterdam", minPrice=0, maxPrice=60000,interior=""):
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

    data = []
    for url in urlList:
        # Fetch webdata
        # parse data and get the following fields, Name, Location, Size, No. of Rooms, Year, Link to property, Postal Code
        # store everything within a pandas dataframe and export the dataframe to an excel file
        try:
            print("Fetching URL: ", url)
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status
            print(response)                        
        except:
            print("Error fetching URL: ", baseUrl)
            continue

fetchData(minPrice=1500, maxPrice=3000)