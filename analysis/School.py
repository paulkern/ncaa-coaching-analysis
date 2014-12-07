import sqlite3 as lite
from collections import defaultdict

class School:

    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.yearlyOverall = {}
        self.offense = {}
        self.defense = {}
        self.staff = defaultdict()
        self.buildYearlyRecord()
        self.buildYearlyStaff()


    def buildYearlyRecord(self):
        """ Query coach.db to get yearly win/loss data for self.name """
        con = lite.connect('coach.db')
        con.text_factory = str
        with con:
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("select * from schools where school = \""+self.name+"\"")
            temp = cur.fetchall()
            for row in temp:
                self.yearlyOverall[row[0]] = {'win': row[2], 'loss': row[3], 'tie': row[4], 'pf': row[6], 'pa': row[7]}


    def buildYearlyStaff(self):
        """ Query coach.db to get list of coaches each year """
        con = lite.connect('coach.db')
        con.text_factory = str
        with con:
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("select * from headCoaches where school = \""+self.name+"\"")
            temp = cur.fetchall()
            for row in temp:
                self.staff[row[2]] = defaultdict(list)
                self.staff[row[2]]['hc'].append(row[0])
                
            cur.execute("select * from allCoaches where school = \""+self.name+"\"")
            temp = cur.fetchall()
            for row in temp:
                if row[3] != 'hc':
                    try:
                        self.staff[row[2]][row[3]].append(row[0])
                    except:
                        self.staff[row[2]] = defaultdict(list)
                        self.staff[row[2]][row[3]].append(row[0])
       
                
    def wins(self, year):
        out = self.yearlyOverall.get(year).get('win')
        return out or 0

    def losses(self, year):
        out =  self.yearlyOverall.get(year).get('loss')
        return out or 0
     
    def ties(self, year):
        out =  self.yearlyOverall.get(year).get('ties')
        return out or 0
        
    def games(self,year):
        return self.wins(year) + self.losses(year) + self.ties(year)
        
    def points_for(self, year):
        return self.yearlyOverall.get(year).get('pf')
        
    def points_against(self, year):
        return self.yearlyOverall.get(year).get('pa')
