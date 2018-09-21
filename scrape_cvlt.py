""" Main Program - CV.LT
Sep17
"""

import requests, re, os, time, datetime, sys
from bs4 import BeautifulSoup
from helpers import *

TEST_RUN = False
PARENT_URL = 'http://www.cv.lt/employee/announcementsAll.do?regular=true&ipp=200'
OUTPUT_FILENAME = "/data/" + timestamp_extension() + ".txt"
LOG_FILENAME = "/log/ads_log_cvlt.txt"
sleep_time = 5  # seconds

outputFilepath = os.getcwd() + OUTPUT_FILENAME
#remove_if_exists(outputFilepath)
logFilepath = os.getcwd() + LOG_FILENAME

running_start_time = time.time()  # for getting elapsed time later
to_log = "Running START time: " + time.ctime()
scrape_log(to_log, logFilepath)
print(to_log)

# get ad count
countsDict = get_counts_cvlt(PARENT_URL)
addPagesCount = countsDict['webpageCount']
estimated_scrape_time = sleep_time * addPagesCount

to_log = "Total ads to scrape: " + str(
    countsDict['adCount']) + ". Estimated time to complete: " + str(
    datetime.timedelta(seconds=estimated_scrape_time)) + "(h:m:s)"
scrape_log(to_log, logFilepath)
print(to_log)

adDataComplete = []

to_log = "---SCRAPING---"
scrape_log(to_log, logFilepath)
print(to_log)

for page in range(addPagesCount + 1):
    urlConstruct = PARENT_URL + '&page=' + str(page)

    # CV.lt
    if page <= addPagesCount:
        # gets job ads data as list of dict entries
        adData = scrape_cvlt(urlConstruct)
        # writes to text file
        append_file(adData, outputFilepath)
        # saves to a list
        for item in adData:
            adDataComplete.append(item)

    # print status info
    to_log = "Page " + str(page + 1) + " of " + str(addPagesCount) + " scraped, " + "total entries: " + str(
        len(adDataComplete))
    scrape_log(to_log, logFilepath)
    print(to_log)
    time.sleep(sleep_time)
    if TEST_RUN:
        break

running_finish_time = time.time()
running_time = running_finish_time - running_start_time

to_log = "---SUMMARY---"
scrape_log(to_log, logFilepath)

to_log = "Completed in " + str(datetime.timedelta(seconds=running_time))
scrape_log(to_log, logFilepath)
print(to_log)

to_log = "Running FINISH time: " + time.ctime()
scrape_log(to_log, logFilepath)
print(to_log)

to_log = "\n\n"
scrape_log(to_log, logFilepath)