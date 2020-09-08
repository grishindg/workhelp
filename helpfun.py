#работает отдельно от fastman
import sqlite3
from openpyxl import load_workbook
import datetime as dt

PATH_TO_DB = './files/events.db'
EXFILE = './files/events.xlsx'
def create_table(db):
	conn = sqlite3.connect(db)
	curs = conn.cursor()
	curs.execute('CREATE TABLE events (name TEXT PRIMARY KEY,\
									   duration TEXT, masters TEXT)')
	conn.commit()
	conn.close()
	print('Создали таблицу')

def insert_todb(db, exfile):
	wb = load_workbook(exfile, read_only=True)
	sheet = wb['events']

	conn = sqlite3.connect(db)
	curs = conn.cursor()

	for i in range(1, 300):
		if sheet[i][1].value == 'stop':
			# print('Достигнут stop')
			break
		conn.execute("INSERT INTO events \
					  VALUES ('{}', '{}', '{}')".format(sheet[i][1].value, 
					   							 	  sheet[i][2].value, 
					   							 	  sheet[i][3].value))
	conn.commit()
	conn.close()
	wb.close()
	print('база данных заполнена')

def stats(db, table):
	conn = sqlite3.connect(db)
	curs = conn.cursor()
	curs.execute('SELECT * FROM {}'.format(table))
	rawarr = curs.fetchall()
	conn.close()
	from fastman import WORKERS
	stat = []
	holidays = []

	for name in WORKERS:
		days = list(range(8,31))
		hours = 0
		for ev in rawarr:
			if name not in ev[3].split(' '):
				continue
			hours += (ev[2] - ev[1])/3600
			day = dt.datetime.fromtimestamp(ev[1])
			if day.day in days:
				days.remove(day.day)
		stat.append(hours)
		holidays.append(days)

	

	for n, h, d in zip(WORKERS, stat, holidays):
		print(n, h, d, len(d))

def rebuilderDB(db, table):
		conn = sqlite3.connect(db)
		curs = conn.cursor()
		curs.execute('SELECT * FROM {}'.format(table))
		rawarr  = curs.fetchall()
		ev_id = 1
		curs.execute('CREATE TABLE сентябрь2 (name TEXT, start REAL, '
					 'finish REAL, members TEXT, notes TEXT,'
					 'evID INT PRIMARY KEY, glID TEXT)')
		for ev in rawarr:
			curs.execute('INSERT INTO сентябрь2 (name, start, finish, members, evID) '
			 			 'VALUES ("{}", {}, {}, "{}", {})'.format(ev[0], ev[1], ev[2], ev[3], ev_id))
			ev_id += 1
		conn.commit()
		conn.close()
		print('готово')

if __name__ == '__main__':
	# create_table(PATH_TO_DB)
	# insert_todb(PATH_TO_DB, EXFILE)
	# stats(PATH_TO_DB, 'сентябрь')
	rebuilderDB(PATH_TO_DB, 'сентябрь')