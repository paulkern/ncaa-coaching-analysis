import sqlite3 as lite
import re, csv, pickle
from School import School
from Coach import Coach

def retrieveMapping(school):
    school = school.strip()
    try:
        return schoolTranslation[school]
    except:
        try:
            return schoolTranslation[school.lower()]
        except:
            errorF.write("lookup error," + school + "\n")
    return school.lower()


def trimCoach(coach):
    coach = coach.replace("\"","").lower()
    coach = re.sub("[^a-z ]", "", coach)
    return coach

def readLineQuoted(line):
    data = line.split(",")
    if(len(data)==12):
        return data
    newData = []
    i = 0
    while i < len(data):
        if (data[i].find("\"")!=-1):
            newData.append(data[i] + "," +data[i+1])
            i += 1
        else:
            newData.append(data[i])
        i+=1
    return newData

def buildDatabase():
    
    global errorF    
    headC = open("headCoaches.csv")
    allC = open("coaches.csv")
    mappingF = open("schoolMapping.csv", 'r')
    errorF = open("newErrors.csv", "w", 1000)

    global schoolTranslation
    schoolTranslation = {}
    for line in mappingF:
        #print(line)
        data = line.split(",")
        temp = data[0]
        if temp[:4] == 'king':
            print (temp, temp.replace("'", ""))
        schoolTranslation[data[1]] = data[0].replace("'", "")
        
        
    headCoaches = [line.split(',') for line in headC]
        
    hc = []

    for row in headCoaches:
        startYear = int(row[2])
        hc.append([trimCoach(row[0]), retrieveMapping(row[1]), startYear, 'hc'])
        endYear = int(row[3])
        if (endYear==-1):
            endYear = 2014
        if (endYear>startYear):
            for n in range(startYear+1, endYear+1):
                #coach, school, year, position
                hc.append([trimCoach(row[0]), retrieveMapping(row[1]), n, 'hc'])
            
    allCoaches = []
    for line in allC:
        row = line.split(',')
        allCoaches.append([trimCoach(row[0]), retrieveMapping(row[1]), row[4], row[5], row[3]])

    ac = []
    for row in allCoaches:
        try:
            startYear = int(row[2])
            ac.append([trimCoach(row[0]), retrieveMapping(row[1]), startYear, row[4]])
            endYear = int(row[3])
            if (endYear==-1):
                endYear = 2014
            if (endYear>startYear):
                for n in range(startYear+1, endYear+1):
                    ac.append([trimCoach(row[0]), retrieveMapping(row[1]), n, row[4]])
        except:
            print(row)
            pass
            
    headC.close()
    allC.close()

    ac = [list(x) for x in set(tuple(x) for x in ac)]
    hc = [list(x) for x in set(tuple(x) for x in hc)]

    schoolF = open('../finalData/warehouse_schools_new.csv', 'r')
    schoolRecords = []
    for line in schoolF:
        row = line.split(',')
        vals = [int(row[1]), retrieveMapping(row[2]), int(row[3]), int(row[4]), int(row[5]), float(row[6]), int(row[7]), int(row[8]), int(row[9]), float(row[11])]
        #print(vals)
        schoolRecords.append(vals)

    stats = []
    statsF = open('../finalData/processedStats.csv', 'r')        
    for l_count, line in enumerate(statsF):
        if(l_count>0):
            row = line.split(',')
            row_vals = [retrieveMapping(row[0]), int(row[1])]
            for i in range(2, len(row)):
                row_vals.append(row[i])
            stats.append(row_vals)
        

    #create database with values
    con = lite.connect('coach.db')
    con.text_factory = str

    with con:
        cur = con.cursor()
        cur.execute("drop table if exists headCoaches")
        cur.execute("drop table if exists allCoaches")
        cur.execute("drop table if exists schools")
        cur.execute("drop table if exists stats")
        cur.execute("drop table if exists newStats")
        cur.execute("drop table if exists oldStats")
        
        cur.execute("create table stats(school text, year int, offPassYd text, offRushYd text, offRushYdAvg text, defPassYd text, defRushYd text, " +
        "defRushYdAvg text, difTakeaways text, offTDpP text, defTDpP text, totPenalties text, offPassYdAvg text, defPassYdAvg text, offTD text, " +
        "defTD text, runAvgoffPassYd text, runAvgoffRushYd text, runAvgoffRushYdAvg text, runAvgdefPassYd text, runAvgdefRushYd text, runAvgdefRushYdAvg text, " +
        "runAvgdifTakeaways text, runAvgoffTDpP text, runAvgdefTDpP text, runAvgtotPenalties text, runAvgoffPassYdAvg text, runAvgdefPassYdAvg text, runAvgoffTD text, runAvgdefTD text)")
                
        cur.execute("create table headCoaches(name text, school text, year int, position text)")
        cur.execute("create table allCoaches(name text, school text, year int, position text)")
        cur.execute("create table schools(year int, school text, win int, loss int, tie int, pct real, pf int, pa int, delta int, runAvgpct real)")
        cur.executemany("insert into headCoaches values(?, ?, ?, ?)", hc)
        cur.executemany("insert into allCoaches values(?, ?, ?, ?)", ac)
        cur.executemany("insert into schools values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", schoolRecords)
        cur.executemany("insert into stats values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", stats)
        cur.execute("create index head_name_index on headCoaches(name)")
        cur.execute("create index all_name_index on allCoaches(name)")
        cur.execute("create index schools_index on schools(school)")
        cur.execute("create index statsSchools on stats(school)")

    errorF.close()
    mappingF.close()
    
def pickleSchools():
    
    school_names = []
    con = lite.connect('coach.db')
    con.text_factory = str
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("select distinct school from schools")
        temp = cur.fetchall()
        for row in temp:
            school_names.append(row[0])
        
    
    schools = {}
    for i, school in enumerate(school_names):
        schools[school] = School(school, i)
    
    pkl = open('schools.pkl', 'wb')
    pickle.dump(schools, pkl)
    pkl.close()
    
def pickleCoaches():
    
    coach_names = []
    con = lite.connect('coach.db')
    con.text_factory = str
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("select distinct name from headCoaches union select distinct name from allCoaches")
        temp = cur.fetchall()
        for row in temp:
            coach_names.append(row[0])
        
    coaches = {}
    for i, coach in enumerate(coach_names):
        coaches[coach] = Coach(coach, i)
    
    supF = open('superiorRelationships.csv', 'r')
    sups = {}
    for row in supF:
        line = row.split(',')
        sups[line[0]] = line[1].rstrip()
    supF.close()
    
    pkl = open('schools.pkl', 'rb')
    schools = pickle.load(pkl)
    pkl.close()
    
    for c in coaches:
        coach = coaches[c]
        coach.buildMentorsList(schools, sups)
    
    pkl = open('coaches.pkl', 'wb')
    pickle.dump(coaches, pkl)
    pkl.close()
    Coach.outF.close()

if __name__ == "__main__":
    buildDatabase()
    pickleSchools()
    pickleCoaches()
