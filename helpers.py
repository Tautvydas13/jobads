#!/usr/local/bin/python
# coding='utf-8'

import requests, re, datetime, sys
from bs4 import BeautifulSoup

"""Definition of helper functions"""

# makes soup
def make_soup(url):
    response = requests.get(url)
    print("status: ", response.status_code, url)
    soup = BeautifulSoup(response.content, "lxml")
    return soup


# removes filename if already exists

def remove_if_exists(filename):
    import os
    try:
        os.remove(filename)
    except OSError:
        pass
    return None


# writes to txt
# input: <list> of dict entries, filename
# output: appending txt file

def append_file(dataList, outFPath):
    with open(outFPath, "ab") as outF:
        for row in dataList:
            for value in row:
                outF.write( value )
                outF.write( "\t".encode('utf-8') )
            outF.write("\n".encode('utf-8'))
    return None


# prints PARENT_URL summary stats
# input: PARENT_URL
# returns: total number of pages that all adds are displayed in

def get_counts_cvonlinelt(PARENT_URL):
    import math
    print("---INITIAL INFO---")
    response = requests.get(PARENT_URL)
    print("status: ", response.status_code, PARENT_URL)
    soup = BeautifulSoup(response.content, "lxml")
    extracted_numbers = soup.find("h1").get_text()
    extracted_numbers = re.findall(r'\d+', extracted_numbers)
    adCountForeign = 0
    for item in extracted_numbers[1:]:
        adCountForeign += int(item)
    adCount = int(extracted_numbers[0]) - adCountForeign
    webpageCount = int(math.ceil(int(adCount) / 50))
    print("Ads found:", adCount, "displayed in", webpageCount, "pages")
    return {'webpageCount': webpageCount,
            'adCount': adCount}


# gets total number of pages containing adds
# input: url
# returns: int

def get_counts_cvlt(PARENT_URL):
    import requests
    from bs4 import BeautifulSoup
    print("---INITIAL INFO---")
    response = requests.get(PARENT_URL)
    print("status: ", response.status_code, PARENT_URL)
    soup = BeautifulSoup(response.content, "lxml")
    webpageCount = int(soup.find("span", class_='paging-top').get_text().split()[2])
    adCount = int(soup.find("span", class_='lgray2').get_text().split()[1].replace('.', ''))
    print("Ads found:", adCount, "displayed in", webpageCount, "pages")
    return {'webpageCount': webpageCount,
            'adCount': adCount}


# appends filename with '_month_day' before file extension
# input: original filename
# returns: (m, d) <tuple>


def get_counts_cvbankaslt(PARENT_URL):
    import requests
    from bs4 import BeautifulSoup
    print("---INITIAL INFO---")
    response = requests.get(PARENT_URL)
    print("status: ", response.status_code, PARENT_URL)
    soup = BeautifulSoup(response.content, "lxml")
    # get webpageCount
    webpageCount = int( soup.find('ul', class_='pages_ul_inner').contents[-2].get_text().strip() )
    # get adCount
    adCountString = soup.find('span', id='filter_statistics').get_text()
    adCount = int( re.search(r'\d+', adCountString).group(0) )
    print("Ads found:", adCount, "displayed in", webpageCount, "pages")
    return {'webpageCount': webpageCount,
            'adCount': adCount}

def get_counts_dirbkitlt(PARENT_URL):
    import requests
    from bs4 import BeautifulSoup
    print("---INITIAL INFO---")
    response = requests.get(PARENT_URL)
    print("status: ", response.status_code, PARENT_URL)
    soup = BeautifulSoup(response.content, "lxml")

    print(soup.prettify())
    sys.exit(13)

    # get webpageCount
    webpageCount = soup.find('div', id='pages').contents
    print(webpageCount)
    sys.exit(13)

    # get adCount
    adCountString = soup.find('span', id='filter_statistics').get_text()
    adCount = int( re.search(r'\d+', adCountString).group(0) )

    print("Ads found:", adCount, "displayed in", webpageCount, "pages")
    return {'webpageCount': webpageCount,
            'adCount': adCount}

# appends filename with '_month_day' before file extension
# input: original filename
# returns: (m, d) <tuple>
def timestamp_extension():
    import datetime
    now = datetime.datetime.now()
    # scraping @ 4am, thus data for previous day activity (i.e. day - 1)
    return str(now.year) + '-' + str(now.month) + '-' + str(now.day) + '_' + str(now.hour) + '-' + str(now.minute)


# writes to txt
# input: <str> text to write to log, <str> filename
# output: appending txt file

def scrape_log(text, outputFilename):
    with open(outputFilename, "a") as outFile:
        outFile.write(text)
        outFile.write("\n")
    return None




def adContentExist(html, tagName, className):
    return html.find_all(tagName, className)


"""Scraper functions - CV.LT"""

# scrapes job add info
# CV.LT
# input: url
# output: list of list entries (len=200)
def scrape_cvlt(url):

    import requests, re, datetime
    from bs4 import BeautifulSoup

    soup = make_soup(url)
    tr = soup.tbody.find_all('tr', class_=['data sponsor', 'data'])

    # initialize returned value
    adValueList = []


    # Data retrieval function descriptions
    def companyNameF(html):
        return html.find("a", itemprop="hiringOrganization").get_text().strip()


    def companyCityF(html):
        return html.find("a", itemprop="").get_text().strip()


    def jobTitleF(html):
        return html.find("a", itemprop="title").get_text().strip()


    def jobViewCountF(html):
        return html.find("span", class_="visited").get_text().replace('.', '')


    def jobDeadlineF(html):
        return html.find_all('td')[-2].get_text().strip()


    def jobPublishedSinceF(html):
        # netipinis html isdestymas, jei paskelbta "Pries X min." arba "Pries X val." <- customInterval
        # tipinis: "Pries X d.", "Pries X men."
        def getIntervalInMinutes(html):
            return html.find("span", class_="timer minutes").get_text()

        def getIntervalInHours(html):
            return html.find("span", class_="timer hours").get_text()

        try:
            customInterval = getIntervalInMinutes(html)
        except:
            try:
                customInterval = getIntervalInHours(html)
            except:
                customInterval = ""

        return html.td.div.contents[0] + customInterval


    def jobUrlF(html):
        return "https://www.cv.lt" + html.find("a", itemprop="title").get("href")

    # loop thru every job entry(table row) in page
    for td in tr:

        # initialize adValues
        companyName = companyCity = jobTitle = jobViewCount = jobDeadline = jobPublished = jobUrl = ''

        # make list/tuple for adValues and corresponding functions to retrieve them
        adValues = [companyName, companyCity, jobTitle, jobViewCount, jobDeadline, jobPublished, jobUrl]
        adValueFunctions = (companyNameF, companyCityF, jobTitleF, jobViewCountF, jobDeadlineF, jobPublishedSinceF, jobUrlF)

        # todo: make assertion that: len(adValues) == len(adValueFunctions), notify otherwise
        # retrieve data or 'error'
        for i in range(len(adValues)):
            try:
                adValues[i] = adValueFunctions[i](td)
            except:
                adValues[i] = 'error'

        # convert output to bytes
        adValuesBytes = []
        for v in adValues:
            adValuesBytes.append( v.encode('utf-8') )

        # add scrape timestamp in bytes
        adValuesBytes.append( datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode('utf-8') )

        adValueList.append(adValuesBytes)

    return adValueList
"""Scraper functions - CVONLINE.LT"""

# scrapes job add info
# CVONLINE.LT
# input: url
# output: list of list entries (len=50)
def scrape_cvonlinelt(tRows):

    import requests, re, datetime
    from bs4 import BeautifulSoup

    # Data retrieval function descriptions
    def companyNameF(html):
        return html.find("span", itemprop="hiringOrganization").a.get_text()

    def companyCityF(html):
        return html.find("span", itemprop="jobLocation").get_text()

    def jobTitleF(html):
        return html.find("a", itemprop="title").get_text()

    def jobViewCountF(html):
        return 'n/a'

    def jobDeadlineF(html):
        return html.find("ul", class_="offer_dates").contents[3]['title'].strip()

    def jobPublishedSinceF(html):
        return html.find("span", itemprop="datePosted")['content']

    def jobUrlF(html):
        return html.find("a", itemprop="title")['href'][2:]

    # initialize returned value
    adValueList = []

    # loop thru every job entry(table row) in page
    for td in tRows:

        # initialize adValues
        companyName = companyCity = jobTitle = jobViewCount = jobDeadline = jobPublished = jobUrl = ''

        # make list/tuple for adValues and corresponding functions to retrieve them
        adValues = [companyName, companyCity, jobTitle, jobViewCount, jobDeadline, jobPublished, jobUrl]
        adValueFunctions = (companyNameF, companyCityF, jobTitleF, jobViewCountF, jobDeadlineF, jobPublishedSinceF, jobUrlF)

        # todo: make assertion that: len(adValues) == len(adValueFunctions), notify otherwise
        # retrieve data or 'error'
        for i in range(len(adValues)):
            try:
                adValues[i] = adValueFunctions[i](td)
            except:
                adValues[i] = 'error'

        # convert output to bytes
        adValuesBytes = []
        for v in adValues:
            adValuesBytes.append( v.encode('utf-8') )

        # add scrape timestamp in bytes
        adValuesBytes.append( datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode('utf-8') )

        adValueList.append(adValuesBytes)

    return adValueList

"""Scraper functions - CVMarket.LT"""

# scrapes job add info
# CVMarket.LT
# input: url
# output: list of list entries (len=25)
def scrape_cvmarketlt(tRows):

    import requests, re, datetime
    from bs4 import BeautifulSoup

    # Data retrieval function descriptions
    def companyNameF(html):
        return html.find("span", class_="f_job_company").get_text()

    def companyCityF(html):
        return html.find("span", class_="f_job_city").get_text()

    def jobTitleF(html):
        return html.find("a", class_='f_job_title').get_text()

    def jobViewCountF(html):
        return 'n/a'

    def jobDeadlineF(html):
        return html.find("td", class_="column5").contents[0].strip()

    def jobPublishedSinceF(html):
        return html.find("td", class_="column1").contents[0].strip()

    def jobUrlF(html):
        return 'www.cvmarket.lt/' + html.find("a", class_='f_job_title')['href']

    # initialize returned value
    adValueList = []

    # loop thru every job entry(table row) in page
    for td in tRows:

        # initialize adValues
        companyName = companyCity = jobTitle = jobViewCount = jobDeadline = jobPublished = jobUrl = ''

        # make list/tuple for adValues and corresponding functions to retrieve them
        adValues = [companyName, companyCity, jobTitle, jobViewCount, jobDeadline, jobPublished, jobUrl]
        adValueFunctions = (companyNameF, companyCityF, jobTitleF, jobViewCountF, jobDeadlineF, jobPublishedSinceF, jobUrlF)

        # todo: make assertion that: len(adValues) == len(adValueFunctions), notify otherwise
        # retrieve data or 'error'
        for i in range(len(adValues)):
            try:
                adValues[i] = adValueFunctions[i](td)
            except:
                adValues[i] = 'error'

        # convert output to bytes
        adValuesBytes = []
        for v in adValues:
            adValuesBytes.append( v.encode('utf-8') )

        # add scrape timestamp in bytes
        adValuesBytes.append( datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode('utf-8') )

        adValueList.append(adValuesBytes)

    return adValueList
"""Scraper functions - CVBankas.LT"""

# scrapes job add info
# CVBankas.LT
# input: url
# output: list of list entries (len=????)
def scrape_cvbankaslt(tRows):

    import requests, re, datetime
    from bs4 import BeautifulSoup

    # Data retrieval function descriptions
    # tame paciame <span> gali buti pateiktas:
    #  -tik imones pavadinimas
    #  -arba dar ir atlyginimo reziai
    def companyNameF(html):
        result = html.find("span", class_="heading_secondary").contents
        if len(result) > 1:
            return result[-1].strip() # kai pateikti ir atlyginimo reziai
        else:
            return result[0].strip()

    def companyCityF(html):
        return html.find("span", class_="list_city").get_text()

    def jobTitleF(html):
        return html.find("h3", class_='list_h3').get_text()

    def jobViewCountF(html):
        return 'n/a'

    def jobDeadlineF(html):
        return 'n/a'

    def jobPublishedSinceF(html):
        try:
            result = html.find("span", class_="txt_list_2").get_text()
        except:
            result = html.find("span", class_="txt_list_important").get_text()
        return result

    def jobUrlF(html):
        return html.find("a", class_='list_a')['href']

    # initialize returned value
    adValueList = []

    # loop thru every job entry(table row) in page
    for td in tRows:

        # initialize adValues
        companyName = companyCity = jobTitle = jobViewCount = jobDeadline = jobPublished = jobUrl = ''

        # make list/tuple for adValues and corresponding functions to retrieve them
        adValues = [companyName, companyCity, jobTitle, jobViewCount, jobDeadline, jobPublished, jobUrl]
        adValueFunctions = (companyNameF, companyCityF, jobTitleF, jobViewCountF, jobDeadlineF, jobPublishedSinceF, jobUrlF)

        # todo: make assertion that: len(adValues) == len(adValueFunctions), notify otherwise
        # retrieve data or 'error'
        for i in range(len(adValues)):
            try:
                adValues[i] = adValueFunctions[i](td)
            except:
                adValues[i] = 'error'

        # convert output to bytes
        adValuesBytes = []
        for v in adValues:
            adValuesBytes.append( v.encode('utf-8') )

        # add scrape timestamp in bytes
        adValuesBytes.append( datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode('utf-8') )

        adValueList.append(adValuesBytes)

    return adValueList
