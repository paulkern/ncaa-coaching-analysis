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

baseURL = "http://www.sports-reference.com"

def writeYearInfo(f, school, link, year, err):
    html = getData(link)
    soup = BeautifulSoup(html)
    table = None
    #find correct data table
    for t in soup.find_all("table"):
        #print("table class is: " + str(t.get("class")))
        try:
            if(t.get("class")[2]=="stats_table"):
                table = t
                break
        except:
            print("not this table")
    if(table is None):
            print("failed to read data for " + link)
            err.write("failed to get table: " + link + "\n")
            err.flush()
            return
    table = table.find("tbody")
    print("writing data for year: " + year)
    f.write(school + ", " + year + ", ")
    #print(school + ", " + year + ", ")
    for r in table.find_all("tr"):
        for td in r.find_all("td"):
            f.write(td.get_text() + ", ")
            #print(td.get_text() + ", ")
    f.write("\n")
    f.flush()
    

def writeSchoolInfo(f, school, link, err):
    html = getData(link)
    soup = BeautifulSoup(html)
    table = None
    for t in soup.find_all("table"):
        print("table class is: " + str(t.get("class")))
        try:
            if(t.get("class")[1]=="stats_table"):
                table = t
                break
        except:
            print("not this table")
    if(table is None):
            print("failed to read data for " + link)
            err.write("failed to get table: " + link + "\n")
            err.flush()
            return
    #loop through all years in school history
    table = table.find("tbody")
    for r in table.find_all("tr"):
        count = 1
        for td in r.find_all("td"):
            if(count==2):
                try:
                    writeYearInfo(f, school, baseURL + td.find("a").get("href"), td.find("a").get_text(), err)
                except:
                    err.write(school + " " + td.find("a").get_text() + "\n")
                    err.flush()
                break
            count += 1

def scrape(restartName=""):
    tableURL = "/cfb/schools/"
    global baseURL
    f = open("schoolsSR.csv","w")
    err = open("errorsSR.txt","w")
    html = getData(baseURL + tableURL)
    soup = BeautifulSoup(html)
    if(restartName!=""):
        skip = True
    else:
        skip = False
    for a in soup.find_all("a"):
        link = a.get("href")
        #explore only links to schools
        if(link!=tableURL and link.find(tableURL)!=-1):
            if(skip and link.find(restartName)!=-1):
                skip = False
            if(not skip):
                print(a.get_text())
                try:
                    writeSchoolInfo(f, a.get_text(), baseURL + link, err)
                except:
                    err.write("failure to write school: " + a.get_text() + "\n")
                    err.flush()
    f.close()
    err.close()

def getData(url):
    data = None
    while(data is None):
        try:
            data = urllib.request.urlopen ( url ).read()
            waitTime()
        except:
            data = None
            print("access denied, waiting a while")
            time.sleep(600)
    return data

def waitTime():
    #be considerate scraper
    time.sleep(2+random.randrange(2))

if __name__ == "__main__":
    import sys
    if(len(sys.argv)>1):
        #restart parameter
        scrape(sys.argv[1])
    else:
        scrape()
