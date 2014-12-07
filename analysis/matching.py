import re

def retrieveMapping(school):
    school = school.strip()
    global schoolTranslation
    try:
        return schoolTranslation[school]
    except:
        try:
            return schoolTranslation[school.lower()]
        except:
            global errorF
            errorF.write("lookup error," + school + "\n")
    return school.lower()


def addCoach(coach, school, year):
    global schoolYear
    school = retrieveMapping(school)
    try:
        temp = schoolYear[school]
    except:
        temp = {}
        schoolYear[school] = temp

    try:
        coach2 = temp[year]
        global errorF
        if(coach2!=coach):
            errorF.write("conflict coach," + school + "," + year + "," + coach2 + "," + coach + "\n")
    except:
        temp[year] = coach

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


errorF = open("errors.csv", "w", 1000)
f = open("tutelage.csv", "w", 1000)
headC = open("headCoaches.csv")
allC = open("coaches.csv")
mappingF = open("schoolMapping.csv")

#get mapping of schools in database to common name

schoolTranslation = {}
for line in mappingF:
    data = line.split(",")
    schoolTranslation[data[1]] = data[0]

schoolYear = {}
for line in headC:
    data = line.split(",")
    startYear = int(data[2])
    endYear = int(data[3])
    if(endYear < 0):
        endYear = 2014
    for y in range(startYear, endYear+1):
        if(y>1960):
            coach = data[0]
            coach = trimCoach(coach)
            addCoach(coach, data[1].strip(), str(y))


prevCoach = ""
tutelage = {}
totalY = 0
for i, line in enumerate(allC):
    if(i > 0):
        data = readLineQuoted(line)
        coach = trimCoach(data[0])
        #write out coach info if we are onto a new coach
        if(prevCoach!=coach):
            if (totalY != 0):
                for key in tutelage:
                    weight=tutelage[key]/float(totalY)
                    f.write(prevCoach + "," + str(weight) + "," + key +"\n")
            totalY = 0
            tutelage = {}

        prevCoach = coach
        
        startYear = int(data[4])
        endYear = int(data[5])
        
        if(endYear < 0):
            endYear = 2014
        if(data[3]!="hc"):
            for y in range(startYear, endYear+1):
                try:
                    school = retrieveMapping(data[1])
                    #print(school)
                    headCoach = schoolYear[school][str(y)]
                    #print(headCoach)
                except:
                    headCoach = -1
                if(headCoach!=-1):
                    try:
                        tutelage[headCoach] = tutelage[headCoach] + 1
                    except:
                        tutelage[headCoach] = 1
                    totalY += 1
if (totalY != 0):
    for key in tutelage:
        weight=tutelage[key]/float(totalY)
        f.write(coach + "," + str(weight) + "," + key +"\n")


errorF.close()
f.close()
allC.close()
mappingF.close()
headC.close()
