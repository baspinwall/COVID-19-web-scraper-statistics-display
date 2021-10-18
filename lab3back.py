#Brian Aspinwall, lab 3
#backend file with database handling
import requests, json, sqlite3
from bs4 import BeautifulSoup
#database only retrieves countries to avoid lookup handling of continents
'''
def combine(oldData):
    newData = [None for x in range(15)]
    for i in range(15):
        if oldData[i] != '' and oldData[i] != ' ' and oldData[i] != 'N/A':
            if i == 1 or i == 14:
                newData[i] = oldData[i]
            else :
                if i == 9 or i == 10 or i == 12:
                    newData[i] = (float)(oldData[i].replace(',','').replace('+','').replace(' ',''))
                else :
                    newData[i] = (int)(oldData[i].replace(',','').replace('+','').replace(' ',''))
    return newData      

page = requests.get('https://www.worldometers.info/coronavirus/')
soup = BeautifulSoup(page.content, "lxml")
fields = soup.find_all('tr')
data = []
start = 0
end = 0
for ind in range(len(fields)):
    if "All" in fields[ind].text:
        start = ind +1
    if "China" in fields[ind].text:
        end = ind +1
        break

for ind in range(start, end):
    data.append(combine(fields[ind].text.split('\n')[1:16]))

with open('data.json', 'w') as fh:
    json.dump(data, fh, indent=3)
'''

data=[]
with open('data.json', 'r') as fh:
    data = json.load(fh)

conn = sqlite3.connect('data.db')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS CoronaDB')
cur.execute('''CREATE TABLE CoronaDB(
    id INTEGER NOT NULL PRIMARY KEY,
    country TEXT,
    totalCases INTEGER,
    newCases INTEGER,
    totalDeaths INTEGER,
    newDeaths INTEGER,
    totalRecovered INTEGER,
    activeCases INTEGER,
    seriousCritical INTEGER,
    casesPer1M REAL,
    deathsPer1M REAL,
    totalTests INTEGER,
    testsPer1M REAL,
    population INTEGER,
    continent TEXT);''')

for d in data:
    cur.execute('''INSERT INTO CoronaDB VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', tuple(d))

conn.commit()
conn.close()