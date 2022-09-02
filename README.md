# Pararius Scraper
Web scaraper for going through Pararius listings and saving them onto an excel file.

If you have any ideas with which you can improve this idea, feel free to create an issue and I hope this helps someone in need ':D

### How To Run
1. Clone the repo

    `git clone https://github.com/vedant15188/parariusScraper`

2. Switch to the correct directory

    `cd ./parariusScraper`

3. (Optional) Initialize a python virtual environment and activate it

    `python -m venv .`

    `./Scripts/activate`

4. Install Requirements

    `pip install -r ./requirements.txt`

5. Run the script

    `python main.py`

6. Deactivate the python virtual environment if applicable. (Only if you did not skip #3)

    `./Scripts/deactivate`

You will see the excel file within the outputs folder.

File Naming Convention: `Pararius_Scrape_{day}-{month}-{year}-{hours}{minutes}{seconds}.xlsx`
