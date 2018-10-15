[![HitCount](http://hits.dwyl.io/middiu/fifa-FUT-Data.svg)](http://hits.dwyl.io/middiu/fifa-FUT-Data)
# FIFA FUT Players Data (Middiu's version)
This script has been created starting from [Kafagy fifa-FUT-Data](https://github.com/kafagy/fifa-FUT-Data) work.

This script version reads and exports extra info from Futhead's website like:
- Players Nation
- Players Work Rate
- Players Strong Foot
- Players Weak Foot
- Players Skill Moves

## What is the purpose of this script?
- The purpose of this repository is to have a script that automatically pulls down all players data from Futhead's website for all FIFA versions starting with FIFA 10.
## How to use it?
- Just run the fifa.py script:
`python fifa.py`
## Players data ouput format:
- After running the script the user will have the data saved in a MySQL database and CSV files.
# Requirements:
- Python 3
- MySQL
- PIP
### You will need to use PIP to install the following libraries:
- pymysql
- bs4
- requests
- pandas
#### Note:
- Input database's host, database name, user and password in the fifa.py connection line.
- Make sure you create tables using the DDL in fifa.sql to be able to correctly encode latin literals when writing to the Database.
