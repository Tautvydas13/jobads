""" Main Program - CVBankas.LT
Nov17
"""

import requests, re, os, time, datetime, sys
from bs4 import BeautifulSoup
from helpers import *

TEST_RUN = False
PARENT_URL = 'https://www.cvbankas.lt/?page='
OUTPUT_FILENAME = "/jobad_scrape/data/" + timestamp_extension() + ".txt"
LOG_FILENAME = "/jobad_scrape/log/ads_log_cvbankaslt.txt"
sleep_time = 5  # seconds

outputFilepath = os.getcwd() + OUTPUT_FILENAME
#remove_if_exists(outputFilepath)
logFilepath = os.getcwd() + LOG_FILENAME

running_start_time = time.time()  # for getting elapsed time later
to_log = "Running START time: " + time.ctime()
scrape_log(to_log, logFilepath)
print(to_log)

# page specific get_counts_... function
countsDict = get_counts_cvbankaslt(PARENT_URL + '1')
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

# loop through pagination
for page in range(addPagesCount + 1):

    # concatenate web url
    urlConstruct = PARENT_URL + str(page)

    # web query
    html = make_soup(urlConstruct)

    # get rows of job-ad data
    adDataRows = adContentExist(html, 'article', 'list_article')

    # break if no more content found
#    if not adDataRows:
#        # print break message
#        to_log = "Page " + str(page + 1) + " has no more content. Program will terminate. " + "Grand total entries: " + str(
#            len(adDataComplete))
#        scrape_log(to_log, logFilepath)
#        print(to_log)
#
#        break

    # gets job ads data
    # NB page specific scrape_... function
    adData = scrape_cvbankaslt(adDataRows)
    # writes to text file
    append_file(adData, outputFilepath)
    # saves to a list
    for item in adData:
        adDataComplete.append(item)

    # print status info
    to_log = "Page " + str(page+1) + " scraped, " + "total entries: " + str(
        len(adDataComplete))
    scrape_log(to_log, logFilepath)
    print(to_log)
    time.sleep(sleep_time)

    # break early of testing
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