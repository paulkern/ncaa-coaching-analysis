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


def writeCoachInfo(f, fs, coach, link):
    #match strip comma from wiki search code
    coach = coach.replace(",","")
    print(coach)
    html = getData(link)
    soup = BeautifulSoup(html)
    for t in soup.find_all("table"):
        width = t.get("width")
        if(width is not None and int(width)==665):
            table = t
            break
    while(len(table.find_all("table")) > 1):
        for t in table.find_all("table"):
            width = t.get("width")
            if(width is not None and int(width)==665 and t.get("cellspacing") is None):
                table = t
                break
    row = 0
    curSchool = None
    startDate = None
    endDate = None
    for r in table.find_all("tr"):
        if(row > 0):
            data = []
            for td in r.find_all("td"):
                data.append(td.get_text().strip())
            #if coach change school, write data
            if(curSchool is None or curSchool!=data[1] or int(data[0])!=(int(endDate)+1)):
                if(curSchool is not None):
                    f.write(coach + ", " + curSchool + ", hc, " + startDate + ", " + endDate + "\n")
                curSchool = data[1]
                startDate = data[0]
            endDate = data[0]
            #write out school data based on each row in table
            fs.write(coach + ", ")
            for i in range(0, len(data)):
                fs.write(data[i] + ", ")
            fs.write("\n")
        row += 1
    f.write(coach + ", " + curSchool + ", hc, " + startDate + ", " + endDate + "\n")

def scrape(restartName=""):
    baseURL = "http://www.cfbdatawarehouse.com/data/coaching/alltime_coaching_records.php?coach="
    start = ord('A')
    f = open("warehouse_new.csv","w")
    fs = open("warehouse_schools_new.csv","w")
    if(restartName!=""):
        skip = True
    else:
        skip = False
    for i in range(start, start+26):
        url = baseURL + chr(i)
        html = getData(url)
        soup = BeautifulSoup(html)
        for a in soup.find_all("a"):
            link = "http://www.cfbdatawarehouse.com/data/coaching/" + a.get("href")
            if(skip):
                if(a.get_text().replace(",","").strip()==restartName):
                    skip = False
            elif(not skip and link.find("coachid")!=-1):
                writeCoachInfo(f, fs, a.get_text(), link)
    f.close()
    fs.close()

def getData(url):
    data = None
    while(data is None):
        try:
            data = urllib.request.urlopen ( url ).read()
            time.sleep(1)
        except:
            data = None
            print("access denied, waiting a while")
            time.sleep(300)
    return data

def waitTime():
    time.sleep(15+random.randrange(10))

if __name__ == "__main__":
    import sys
    if(len(sys.argv)>1):
        scrape(sys.argv[1])
    else:
        scrape()
