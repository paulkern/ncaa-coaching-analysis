import urllib
import urllib.parse
import urllib.request
import json as m_json
import time
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
import random
import mechanicalsoup

def getURLapi(query=""):
    if(query==""):
        query = input ( 'Query: ' )
    query = query + " football coach wiki"
    query = urllib.parse.urlencode ( { 'q' : query } )
    i=0
    #default number of google searches returned
    increment = 4
    while(True):
        json = None
        response = urllib.request.urlopen ( 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&'+query+"&start="+str(i))
        print('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&'+query+"&start="+str(i))
        json = m_json.loads ( response.read().decode() )
        print(json)
        results = json [ 'responseData' ] [ 'results' ]
        for result in results:
            title = result['title']
            url = result['url']   # was URL in the original and that threw a name error exception
            #print ( title + '; ' + url )
            if(url.find("wikipedia")!=-1):
                print("Found URL: " + url)
                return url
        i+=increment
        time.sleep(10)
        if(i>=20):
            return ""

def getURL(query=""):
    print("initial query is: " + query)
    if(query==""):
        query = input ( 'Query: ' )
    n = query.split(" ")
    query = query + " football coach wiki"
    query = urllib.parse.urlencode ( { 'q' : query } )
    i=0

    browser = mechanicalsoup.Browser()
    
    #default number of google searches returned
    increment = 10
    while(True):
        time.sleep(30 + random.randrange(20))
        url = 'https://www.google.com/search?q=' + query + "&oq=" + query
        response = browser.get(url)
        #print(response.soup.prettify().encode("utf-8").decode("us-ascii", "ignore"))
        for result in response.soup.find_all('a'):
            try:
                url = result.get("href")
                if(url is not None and url.find("wikipedia")!=-1):
                    index1 = url.find("http://en.wiki")
                    url = url[index1:]
                    index = url.find("&")
                    temp = url.find("%")
                    if( index == -1 or (temp!=-1 and temp < index)):
                        index = temp
                    if(index!=-1):
                        url = url[:index]
                    count = 0
                    for t in n:
                        if(url.find(t)!=-1):
                            print("matched in url: " + t)
                            count += 1
                    if(count > 1):
                        print(url)
                        return url
            except:
                print('didn\'t have a href')
        i+=increment
        if(i>=20):
            return ""

def gettext(elem):
    text = elem.text or ""
    for subelem in elem:
        text = text + gettext(subelem)
        if subelem.tail:
            text = text + subelem.tail
    return text

def getYears(text):
    """ returns array with rows=lines in text
        2 columns for start and end year """
    lines = text.split("\n")
    dates = []
    count = 0
    for line in lines:
        line = re.sub("[^0-9 ]", "", line)
        words = line.split(" ")
        first = -1
        second = -1
        for word in words:
            word = word.strip()
            if len(word) > 3:
                first = int(word[0:4])
                try:
                    second = int(word[4:])
                except:
                    if(count >= len(lines)-1):
                        second = -1
                    else:
                        second = first
            count+=1
        dates.append([first, second])
    return dates

def parsePosition(text):
    text = text.lower()
    text = text.replace("co-", "")
    if(text.find("offensive coordinator")!=-1 or text.find("(oc")!=-1):
        return "oc"
    if(text.find("defensive coordinator")!=-1 or text.find("(dc")!=-1):
        return "dc"
    if(text.find("running")!=-1 or text.find("(rb")!=-1):
        return "rb"
    if((text.find("defensive")!=-1 and text.find("back")!=-1) or text.find("(db")!=-1 or text.find("secondary coach")!=-1 or text.find("(sc)")!=-1):
        return "db"
    if((text.find("defensive")!=-1 and text.find("line")!=-1) or text.find("(dl")!=-1 or text.find("(de")!=-1 or text.find("(dt")!=-1):
        return "dl"
    if((text.find("offensive")!=-1 and text.find("line")!=-1) or text.find("(ol")!=-1):
        return "ol"
    if(text.find("linebacker")!=-1 or text.find("(lb")!=-1):
        return "lb"
    if(text.find("wide")!=-1 or text.find("receiver")!=-1 or text.find("(wr")!=-1):
        return "wr"
    if(text.find("quarterback")!=-1 or text.find("(qb")!=-1):
        return "qb"
    if(text.find("graduate")!=-1 or text.find("(ga")!=-1 or text.find("unpaid asst")!=-1 or text.find("assistant")!=-1):
        return "ga"
    if((text.find("special")!=-1 and text.find("teams")!=-1) or text.find("(st")!=-1):
        return "st"
    else:
        return "hc"

def getPositions(text):
    text = text.lower()
    lines = text.split("\n")
    firstPos = False
    multiLineType = False
    count = 0
    positions = []
    for line in lines:
        print(line)
        if(not (count==0 and line.find("career")!=-1)):
            if(line.find("(")==-1):
                firstPos = True
                if(count == 0):
                    multiLineType = True
                    #means that each stop is stored like john harbaugh's info
            if(not multiLineType or (multiLineType and firstPos)):
                #for now care only about first position at a given stop
                pos = parsePosition(line)
                print(pos)
                positions.append(pos)
                firstPos = False
        count += 1
    return positions

def getWikiInfo(url):
    html = urllib.request.urlopen ( url ).read()
    root = ET.fromstring(html)
    #will have to have different cases here to account for different formatting types
    for table in root.iter("table"):
        if(table.get("class") is not None and table.get("class").find("infobox")!=-1):
            isNext = False
            isNextCarroll = False
            counter = -1
            #search children once we have the infobox
            for tr in table.iter("tr"):
                #handles pages similar to jim harbaugh
                if(counter==0):
                    stuff = gettext(tr).encode("ascii", 'ignore').decode("ascii").strip()
                    print(stuff)
                    dates = getYears(stuff)
                    print(dates)
                    positions = getPositions(stuff)
                    print(positions)
                    return stuff, positions, dates
                #handles cases similar to paul johnson page
                if(isNext):
                    print(text)
                    dates = gettext(tr.find("th").find("span"))
                    places_span = tr.find("td").find("span")
                    places = gettext(places_span)
                    dates = getYears(dates.encode("ascii", 'ignore').decode("ascii"))
                    places = places.encode("ascii", 'ignore').decode("ascii")
                    positions = getPositions(places)
                    print(dates)
                    print(places)
                    print(positions)
                    return places, positions, dates
                if(isNextCarroll):
                    print(text)
                    listtd = tr.findall("td")
                    dates = gettext(listtd[0])
                    places = gettext(listtd[1])
                    dates = getYears(dates.encode("ascii", 'ignore').decode("ascii"))
                    places = places.encode("ascii", 'ignore').decode("ascii")
                    positions = getPositions(places)
                    print(dates)
                    print(places)
                    print(positions)
                    return places, positions, dates
                temp = tr.find("th")
                if(temp is not None and temp.text is not None):
                    text = gettext(temp).lower()
                    if(text.find("coach")!=-1 and (text.find("career")!=-1 or text.find("team")!=-1)):
                        isNext=True
                        print("triggered is next")
                    elif(text.find("career")!=-1 and text.find("history")!=-1):
                        print("counting down")
                        counter = 4
                else:
                    text = gettext(tr).lower()
                    if(text.find("coach")!=-1 and (text.find("career")!=-1 or text.find("team")!=-1)):
                        isNextCarroll=True
                        print("triggered is next")
                counter-=1
#notes for wikipedia scraping:
#sideline formatting contains keywords: career, coach,
#in table tr, schools can be subtable
#also year and school can be same line of text or in different matching sub-tables

def scrapeCoaches(csv):
    """ need to start with csv of coach names """
    f = open(csv)
    output = open("scrapedOutput.csv", "w")
    errorFile = open("errors.txt","w")
    for line in f:
        line = line.strip().replace(",", "").replace("\"","")
        url = getURL(line)
        if(url!=""):
            try:
                blah = getWikiInfo(url)
                if(blah is not None):
                    places = blah[0]
                    positions = blah[1]
                    dates = blah[2]
                    places = places.split("\n")
                    if(len(positions) > 0 and len(places) > 0 and len(dates) > 0):
                        while(len(positions)>len(dates)):
                            dates.append([-1,-1])
                        while(len(dates)>len(positions)):
                            positions.append(positions[-1])
                            places.append(places[-1])
                        for i in range(0,len(positions)):
                            output.write(line + ", " + places[i] + ", " + str(positions[i]) + ", " + str(dates[i]) + "\n")
            except:
                errorFile.write("Could not get data for url: " + url)
            
    f.close()
    output.close()
    errorFile.close()

if __name__ == "__main__":
    import sys
    if(len(sys.argv) < 2):
        print("please provide csv file of coaching names as input")
    else:
        scrapeCoaches(sys.argv[1])
    #getURL(sys.argv[1])
