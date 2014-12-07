import sqlite3 as lite
from collections import defaultdict
import math

class Coach:

    outF = open("scoreCheck.csv","w")
    
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.job_history = {}
        self.mentors = defaultdict(list)
        self.buildJobHistory() # job_history is a dictionary of form {int year: string school, string position)}
        self.coachingScore = self.calcCoachingScore() #simple numeric evaluation of coaches performance
        self.coworkers = [] # coworkers is array of form[stop#] = (object(school), set(superiors), set(coworkers), set(inferiors))
        #self.findCoworkers()
        self.initYears()
        self.treePerf = -10
        self.treeInfPerfList = []

    def initYears(self):
        self.yearsHC = len(self.getHCYears())
        temp = self.getActiveYears()
        self.yearsTotal = len(temp)
        self.firstYear = temp[0]
        self.lastYear = temp[-1]
        

    def buildJobHistory(self):
        """ Query coach.db to get a complete job history for self.name """
        con = lite.connect('coach.db')
        con.text_factory = str
        with con:
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("select distinct * from headCoaches where name = \""+self.name+"\" union select distinct * from allCoaches where name =\""+self.name+"\"")
            jobhist = cur.fetchall()

        for row in jobhist:
            self.job_history[row['year']] = {'school': row['school'], 'position': row['position']}

    def getSchoolByYear(self, year):
        return self.job_history.get(year).get('school')
        
    def getPositionByYear(self, year):
        return self.job_history.get(year).get('position')
        
    def getActiveYears(self):
        years = []
        for key in self.job_history:
            years.append(key)
        years.sort()
        return years
        
    def getHCYears(self):
        years = []
        for year in self.job_history:
            job = self.job_history[year]
            if job['position'] == 'hc':
                years.append(year)
        years.sort()
        return years

    def getStats(self, school, year, cur):
        stats = {}
        query = "select sum(win), sum(loss), sum(tie), avg(pct), avg(runAvgpct) from schools where year = '" + str(year) +"' and school = \"" + school + "\" group by school"
        #print(query)
        cur.execute(query)
        row = cur.fetchone()
        if(row != None):
            #print(row.keys())
            #print(row)
            wins = float(row[0])
            losses = float(row[1])
            ties = float(row[2])
            runAvgpct = float(row[4])
            pct = wins / (wins + losses + ties)
            stats["pct"] = pct
            stats["runAvgpct"] = runAvgpct

        query = "select * from stats where year = '" + str(year) +"' and school = \"" + school + "\""
        cur.execute(query)
        row = cur.fetchone()
        if(row != None):
            for key in row.keys():
                if(key!="year" and key!="school"):
                    stats[key] = row[key]
        #print(stats)
        return stats

    def getPrevStats(self, school, year, cur):
        """ return all of the important statistics of this school at given year """
        year -= 1
        return self.getStats(school, year, cur)

    def calcCoachingScore(self):
        """ calculate score based on predetermined weights """
        import sqlite3 as lite
        import xlrd
        import os
        
        con = lite.connect('coach.db')
        con.text_factory = str

        #dictionary by position (weight (float), stat_weights (dictionary by field (values = weight (float)))
        pos_weights = {}
        weightsF = open('../finalData/ScoringWeights.csv', 'r')
        for line in weightsF:
            row = line.split(",")
            stats_weights = {}
            for i in range(int(math.floor((len(row)-3)/2))):
                field = row[3+2*i]
                if(field == ""):
                    break
                weight = float(row[4+2*i])
                stats_weights[field] = weight 
            pos_weights[row[0]] = (float(row[2]), stats_weights)            

        prevSchool = None
        prevYear = None
        prevPos = None

        temp_weights = 0
        temp_improvement = 0
        improvement = 0
        weights = 0

        years = self.getActiveYears()
        foundYears = 0
        for year in years:
            with con:
                con.row_factory = lite.Row
                cur = con.cursor()
                details = self.job_history[year]
                school = details['school']
                pos = details['position']
                #print(details)

                if(prevSchool == None):
                    prior_stats = self.getPrevStats(school,year, cur)
                    temp_pos_weights = pos_weights[pos]
                    startYear = year
                
                #if school, position or non-sequential year changes recalc weight
                if( (prevSchool!=None and school!=prevSchool) or (prevYear!=None and year!=prevYear+1) or (prevPos!=None and pos!=prevPos)):
                    #if poor fit school ( < 3yr) , downweight achievements
                    if(prevYear - startYear < 3):
                        temp_weights *= .5
                        temp_improvement *= .5
                    #add weights and improvements for coaching score calculation
                    weights += temp_weights*temp_pos_weights[0]
                    improvement += temp_improvement*temp_pos_weights[0]
                    #reset temp information
                    startYear = year
                    temp_weights = 0
                    temp_improvement = 0
                    temp_pos_weights = pos_weights[pos]
                    #stats of school prior to this coach taking job
                    prior_stats = self.getPrevStats(school,year, cur)

                temp_stat_weights = 0
                year_improvements = 0

                current_stats = self.getStats(school, year, cur)
                #print(current_stats)
                if(current_stats!={}):
                    foundYears += 1
                    #total up improvements (divide by prev_stats values) and weights that exist in results
                    #if missing in prior_stats, then we also can't count weight of that field in temp_stat_weights
                    for statName in temp_pos_weights[1]:
                        isMinus = statName.find("-")>-1
                        isRaw = statName.find("raw")==0
                        trimmed = statName
                        if(isMinus):
                            trimmed = trimmed[:-1]
                        if(isRaw):
                            trimmed = trimmed[3:]
                        if(trimmed in current_stats):
                            raw = current_stats[trimmed]
                            runAvg = current_stats["runAvg"+trimmed]
                            if(raw!="" and runAvg!=""):
                                #print(str(year) + " statName: " + statName + " raw: " + str(raw) + " run: " + str(runAvg))
                                temp_stat_weights += temp_pos_weights[1][statName]
                                if(isRaw):
                                    imp = float(raw)
                                    imp -= 0.5
                                else:
                                    if(float(runAvg) == 0):
                                        if(float(raw) > 0):
                                            imp = .05
                                        else:
                                            imp = 0
                                    else:
                                        imp = (float(raw)-float(runAvg))/float(runAvg)
                                if(isMinus):
                                    imp *= -1
                                imp = math.atan(12*imp)
                                imp /= (math.pi/2)
                                year_improvements += imp*temp_pos_weights[1][statName]
                
                temp_weights += temp_stat_weights
                temp_improvement += year_improvements

                prevSchool = school
                prevPos = pos
                prevYear = year

        #output statistics for last coaching stop
        #if poor fit school ( < 3yr) , downweight achievements
        if(prevYear - startYear < 3):
            temp_weights *= .5
            temp_improvement *= .5
        #add weights and improvements for coaching score calculation
        weights += temp_weights*temp_pos_weights[0]
        improvement += temp_improvement*temp_pos_weights[0]
        
        if(weights == 0):
            score = 0
        else:
            score = improvement/weights
        Coach.outF.write(self.name + "," + str(score) + "," + str(foundYears) + "\n")
        #print(score)
        return score
    
    def buildMentorsList(self, schools, sups):
        self.mentors = defaultdict(list)
         
        for year in self.job_history:
            job = self.job_history[year]
            if job.get('position') != 'hc':
                sup_pos = sups.get(job.get('position'))
                sch = schools.get(job.get('school'))
                if sch is not None:
                    sup = sch.staff.get(year).get(sup_pos)
                    if sup is not None:
                        self.mentors[sup[0]].append((sch.name, year, job.get('position')))
    
    def getTotalSubordinateYears(self):
        numYears = 0.0
        for mentor in self.mentors:
            tenures = self.mentors[mentor]
            for job in tenures:
                if job[0][-2:] != 'hs':
                    numYears += 1.0
        return numYears
        
    def getWinPct(self, schools):
        # assuming we only want pct for aggregate hc positions
        years_hc = self.getHCYears()
        wins, games = (0.0, 0.0)
        for year in years_hc:
            school = self.job_history.get(year).get('school')
            try:
                wins += schools.get(school).wins(year)
                games += schools.get(school).games(year)
            except:
                pass #ignore schools for which we have no data
                
        try:
            return wins/games
        except:
            return 'no data'

    def getTreePerf(self, coaches):
        #coaches is dict of coaches by name
        if(self.treePerf != -10):
            return self.treePerf
        #brute force method and designed to avoid cycles in tree
        exploredCoaches = set()
        exploredCoaches.add(self.name)
        stack = []
        stack.append(self.name)
        self.treeInfPerfList = []
        while(len(stack)>0):
            #get this coach from stack
            sc = coaches[stack.pop(-1)]
            #don't add coaches with 0 score because they likely didn't have the information needed to calculate
            if(sc.coachingScore != 0):
                self.treeInfPerfList.append(sc.coachingScore)
            #get inferiors at each job
            for temp in sc.coworkers:
                #print(temp)
                for coach in temp["inferiors"]:
                    if(coach not in exploredCoaches):
                        stack.append(coach)
                        exploredCoaches.add(coach)

        #get representative value by grabbing median of all children values
        self.treeInfPerfList.sort()
        l = len(self.treeInfPerfList)
        if(l==0):
            self.treePerf = 0
        elif(l%2==1):
            self.treePerf = self.treeInfPerfList[l//2]
        else:
            self.treePerf = ( self.treeInfPerfList[l//2] + self.treeInfPerfList[l//2-1] ) / 2.0
        f = open("coachingTreePerf.csv", "a")
        f.write(self.name + "," + str(self.treePerf) + "," + str(len(self.treeInfPerfList)) + "\n")
        f.close()
        return self.treePerf
                                
    def findCoworkers(self):
        """ Get list of coworkers by job ordering """
        import sqlite3 as lite
        import xlrd
        import os

        book = xlrd.open_workbook("superiorRelationships.xlsx")
        sh = book.sheet_by_index(0)
        inf_sup = {}
        sup_inf = {}

        for rx in range(1,sh.nrows):
            sup = sh.row(rx)[1].value.encode('ascii','ignore').decode()
            inf = sh.row(rx)[0].value.encode('ascii','ignore').decode()
            inf_sup[inf] = sup
            try:
                sup_inf[sup].add(inf)
            except:
                sup_inf[sup] = set()
                sup_inf[sup].add(inf)

        #print(sup_inf)
        #print(inf_sup)


        self.coworkers = []

        con = lite.connect('coach.db')
        con.text_factory = str

        prevSchool = None
        prevYear = None
        prevPos = None
        
        temp = {}
        temp["school"] = ""
        temp["superiors"] = set()
        temp["coworkers"] = set()
        temp["inferiors"] = set()

        for year in self.getActiveYears():
            with con:
                con.row_factory = lite.Row
                cur = con.cursor()
                details = self.job_history[year]
                #print(details)
                school = details['school']
                pos = details['position']

                temp["school"] = school


                #if school, position or non-sequential year changes then go ahead and append the temporary dictionary to the final array
                if( (prevSchool!=None and school!=prevSchool) or (prevYear!=None and year!=prevYear+1) or (prevPos!=None and pos!=prevPos)):
                    self.coworkers.append(temp)

                prevSchool = school
                prevPos = pos
                prevYear = year
                
                query = "select distinct * from headCoaches where year = '"
                query += str(year)
                query += "' AND school = \""
                query += school
                query += "\" union select distinct * from allCoaches where year = '"
                query += str(year)+"' AND school = \""
                query += school + "\""
                cur.execute(query)
                temp_q = cur.fetchall()
                if(pos=="hc"):
                    for row in temp_q:
                        if(row[-1] != "hc"):
                            temp["inferiors"].add(row[0])
                else:
                    for row in temp_q:
                        try:
                            inf_set = sup_inf[pos]
                        except:
                            inf_set = None
                        
                        if(row[-1]=="hc" or row[-1]==inf_sup[pos]):
                            temp["superiors"].add(row[0])
                        elif(inf_set!=None and row[-1] in inf_set):
                            temp["inferiors"].add(row[0])
                        elif(row[0]!=self.name):
                            temp["coworkers"].add(row[0])

        #write last school
        self.coworkers.append(temp)
        
if __name__ == "__main__":
    import pickle, json
    from School import School
    pkl = open('coaches.pkl', 'rb')
    coaches = pickle.load(pkl,encoding="UTF8")
    pkl.close()
    for coach in coaches:
        temp = coaches[coach]
        temp.treePerf = -10
        temp.treeInfPerfList = []
        temp.initYears()
    for coach in coaches:
        if(coach=="kelly chip"):
            
            temp = coaches[coach]
            #print(temp.job_history)
            temp.calcCoachingScore()
            Coach.outF.close()
            #temp.getTreePerf(coaches)
        

    #pkl = open('coaches_new.pkl', 'wb')
    #pickle.dump(coaches, pkl)
    #pkl.close()
    
