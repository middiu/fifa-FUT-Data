import re
import time
import requests
import pandas as pd
import pymysql.cursors
from bs4 import BeautifulSoup
import sys

# Runtime start
start = time.clock()
print(start)

# Connect to the database
connection = pymysql.connect(user='epetrang', password='Emilio123!', host='127.0.0.1', db='FUTHEAD', cursorclass=pymysql.cursors.DictCursor, charset='UTF8')
cursor = connection.cursor()

tiers = [
    'gold',
    'silver',
    'bronze'
]

fifa = {
    #'10': 'FIFA10',
    #'11': 'FIFA11',
    #'12': 'FIFA12',
    #'13': 'FIFA13',
    #'14': 'FIFA14',
    #'15': 'FIFA15',
    #'16': 'FIFA16',
    #'17': 'FIFA17',
    #'18': 'FIFA18',
    '19': 'FIFA19'
}

for key, value in fifa.items():
	print(key, value)
for key, value in fifa.items():
    print('Doing FIFA ' + key)

    # Truncating table before inserting data into the table
    cursor.execute('TRUNCATE TABLE FUTHEAD.{};'.format(value))
    cursor.execute('TRUNCATE TABLE FUTHEAD.NATIONS;')

    # Looping through all nation pages
    nations = []
    flagidreg = r"\/(\d+)\.png$"
    FutHeadNations = requests.get('https://www.futhead.com/' + key + '/nations/')
    bs = BeautifulSoup(FutHeadNations.text, 'html.parser')
    NatTotalPages = int(re.sub('\s +', '', str(bs.find('span', {'class': 'font-12 font-bold margin-l-r-10'}).get_text())).split(' ')[1])
    print('Number of pages to be parsed for Nations: ' + str(NatTotalPages))
    for page in range(1, NatTotalPages + 1):
        FutHeadNations = requests.get('https://www.futhead.com/' + key + '/nations/?page='+str(page))
        bs = BeautifulSoup(FutHeadNations.text, 'html.parser')
        Names = bs.findAll('span', {'class': 'player-name'})
        Flags = bs.findAll('img', {'class': 'player-image'})
        natlines = len(bs.findAll('li', {'class': 'list-group-item list-group-table-row player-group-item dark-hover'}))
        for i in range(natlines):
            n = []
            n.append(Names[i].get_text())
            curflag = Flags[i].get("src")
            natid = re.findall(flagidreg, curflag)[0]
            try:
                n.append(re.findall(flagidreg, curflag)[0])
            except IndexError:
                n.append('-1')
            nations.append(n)
        print('Nations page ' + str(page) + ' is done!')
        
    # Inserting data into its specific table
    for nation in nations:
        cursor.execute('''
              INSERT INTO NATIONS (
                  NAME,
                  CODE
              ) VALUES (%s, %s)
        ''', (nation[0], int(nation[1])))
    
    connection.commit()
    print('All Nations saved into DB.')

    # List Intializations
    players = []
    attributes = []
    extraattributes = []

    # Looping through all pages to retrieve players stats and information
    for tier in tiers:
        FutHead = requests.get('https://www.futhead.com/' + key + '/players/?level=' + tier + '&bin_platform=ps')
        bs = BeautifulSoup(FutHead.text, 'html.parser')
        TotalPages = int(re.sub('\s +', '', str(bs.find('span', {'class': 'font-12 font-bold margin-l-r-10'}).get_text())).split(' ')[1])
        print('Number of pages to be parsed for FIFA ' + key + ' ' + tier + ' level players: ' + str(TotalPages))
        for page in range(1, TotalPages + 1):
            FutHead = requests.get('http://www.futhead.com/' + key + '/players/?page=' + str(page) + '&level=' + tier + '&bin_platform=ps')
            #FutHead = requests.get('https://www.futhead.com/19/players/?name=insigne&bin_platform=pc')
            
            bs = BeautifulSoup(FutHead.text, 'html.parser')
            Players = bs.findAll('li', {'class': 'list-group-item list-group-table-row player-group-item dark-hover'})
            num = len(Players)

            # Parsing all players information
            for i in range(num):
                p = []
                Name = Players[i].find('span', {'class': 'player-name'})
                Information = Players[i].find('span', {'class': 'player-club-league-name'})
                p.append(Name.get_text())
                strong = Information.strong.extract()
                try:
                    p.append(re.sub('\s +', '', str(Information.get_text())).split('| ')[1])
                except IndexError:
                    p.append('')
                try:
                    p.append(re.sub('\s +', '', str(Information.get_text())).split('| ')[2])
                except IndexError:
                    p.append('')
                #getting Flag id
                Nation =  Players[i].find('img', {'class': 'player-nation'})

                curflag = Nation.get("data-src")
                natid = re.findall(flagidreg, curflag)[0]
                cursor.execute("SELECT NAME FROM futhead.nations where CODE = {};".format(int(natid)))
                nations = cursor.fetchall()
                try:
                    p.append(nations[0].get("NAME"))
                except IndexError:
                    p.append('')
                p.append(strong.get_text())
                p.append(tier.capitalize())
                Rating = Players[i].find('span', {'class': re.compile('revision-gradient shadowed font-12')})
                p.append(Rating.get_text())
                players.append(p)

                es = []
                ExtraPlayerStats = Players[i].find('span', {'class': 'player-right slide hidden-sm hidden-xs'})
                EStats = ExtraPlayerStats.findAll('span', {'class':'player-stat'})
                for j in range(len(EStats)):                 
                    stat = EStats[j]

                    if stat.find('span', {'class': 'value'}) is None:
                        es.append('')
                    else:
                        if stat.find('span', {'class': 'value'}).get_text() == 'None':
                            es.append('0')
                        else:
                            es.append(stat.find('span', {'class': 'value'}).get_text())
                extraattributes.append(es)
                Stats = Players[i].findAll('span', {'class': 'player-stat stream-col-60 hidden-md hidden-sm'})

                # Parsing all players stats
                temp = []
                for stat in Stats:
                    if stat.find('span', {'class': 'value'}) is None:
                        temp.append('0')
                    else:
                        temp.append(stat.find('span', {'class': 'value'}).get_text())
                attributes.append(temp)
            print('Page ' + str(page) + ' is done!')

    # Inserting data into its specific table
    for player, attribute, extraattribute in zip(players, attributes, extraattributes):
        cursor.execute('''
              INSERT INTO FUTHEAD.{} (
                  NAME,
                  CLUB, 
                  LEAGUE,
                  NATION,
                  POSITION,
                  TIER,
                  RATING,
                  PACE,
                  SHOOTING, 
                  PASSING,
                  DRIBBLING,
                  DEFENDING,
                  PHYSICAL,
                  WORKRATE,
                  STRONGFOOT,
                  WEAKFOOT,
                  SKILLMOVES
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s)
        '''.format(value), (*player, *attribute, *extraattribute))

    # Dumping the lines into a csv file
    pd.read_sql_query('SELECT * FROM FUTHEAD.{};'.format(value), connection).to_csv(value + '.csv', sep=',', encoding='utf-8', index=False)

    # Commit MYSQL statements
    connection.commit()

# Closing connection to the DB and closing csv file
connection.close()

# Runtime end
print(time.clock() - start)