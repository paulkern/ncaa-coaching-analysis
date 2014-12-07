import pickle, json, csv
from School import School
from Coach import Coach
import sqlite3 as lite
from collections import defaultdict

pkl = open('coaches.pkl', 'rb')
coaches = pickle.load(pkl,encoding="UTF8")
pkl.close()
pkl = open('schools.pkl', 'rb')
schools = pickle.load(pkl)
pkl.close()

def getChildren(coach):
    children = []
    coach.findCoworkers()
    for job in coach.coworkers:
        for c in job.get('inferiors'):
            children.append(c)
    return list(set(children))

def coachJSONTree(coach, parent=None, depth=0):
    tree = defaultdict(dict)
    tree['name'] = coach.name
    tree['parent'] = parent
    children = getChildren(coach)
    if depth == 6:
        tree['children'] = children
    else:
        depth += 1
        if len(children) > 0:
            tree['children'] = []
            for child in children:
                if coaches.get(child):
                    tree.get('children').append(coachTree(coaches.get(child), coach.name, depth))
            return tree
        else:
            return tree


edges = [] 
for name in iter(coaches):
    coach = coaches[name]
    coach.initYears()
    y = coach.getTotalSubordinateYears()
    for mentor in coach.mentors:
        tenure = coach.mentors[mentor]
        edge = {'source': coach.id, 'weight': len(tenure)/y, 'target': coaches[mentor].id, 'num_seasons': len(tenure), 'school': tenure[0][0]}
        edges.append(edge)
        
coach_by_id = []
con = lite.connect('coach.db')
con.text_factory = str
with con:
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("select distinct name from headCoaches union select distinct name from allCoaches")
    temp = cur.fetchall()
    for row in temp:
        coach_by_id.append(row[0])
        
coach_by_id.sort(key=lambda x: coaches[x].id) # Shouldn't be necessary but just in case
nodes = []
for i, coach in enumerate(coach_by_id):
    c = coaches.get(coach)
    nodes.append({'coach_id': i, 'name': coach, 'win_pct': c.getWinPct(schools),
                  'yearsHC': c.yearsHC, 'yearsTotal':c.yearsTotal, 'firstYear':c.firstYear,
                  'lastYear':c.lastYear, 'coachingScore':c.coachingScore})
    
data = {'links': edges, 'nodes': nodes}
with open('data.json', 'w') as jsonFile:
    json.dump(data, jsonFile, sort_keys = True, indent = 4, ensure_ascii = False)

ranks = []
with open('./PageRankCalc/pageRanks.csv', 'r') as csvfile:
    next(csvfile)
    reader = csv.reader(csvfile)
    for row in reader:
        ranks.append((int(row[0]), float(row[1])))

ranks.sort(key=lambda x: x[1], reverse=True)
for coach_id in [x[0] for x in ranks[:50]]:
    tree = coachJSONTree(coaches.get(coach_by_id[coach_id]))
    with open(coach.name+'.json', 'w') as jsonFile:
        json.dump(tree, jsonFile, sort_keys=True, indent=4, ensure_ascii=False)

