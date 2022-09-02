# Pararius Scraper
Web scaraper for going through Pararius listings and saving them onto an excel file.

### How To Run
1. Clone the repo
`git clone https://github.com/vedant15188/parariusScraper`

2. Switch to the correct directory and initialize a python virtual environment
`cd ./parariusScraper`

3. (Optional) Initialize virtual environment and activate it
`python -m venv .`
`./Scripts/activate`

4. Install Requirements
`pip install -r ./requirements.txt`

5. Run the script
`python main.py`

You will see the excel file within the outputs folder.
File Naming Convention: `Pararius_Scrape_{day}-{month}-{year}-{hours}{minutes}{seconds}.xlsx`