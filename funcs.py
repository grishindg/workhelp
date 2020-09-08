import re
import sqlite3

dateRe = re.compile(r'([0-3]?\d) ((?:[0-1]?[0-9]|2[0-4])[0-5]\d) ((?:[0-3]?\d) )?((?:[0-1]?[0-9]|2[0-4])[0-5]\d)')

class TotEvents():
	def __init__(self, name, start, finish, members, notes = ''):
		self.evID = 0
		self.gcId = ''
		self.name = name
		self.start = start
		self.finish = finish
		self.members = members
		self.notes = notes

class DBwriter():
	'''класс для работы с базой данных'''
	def __init__(self, db):
		self.db = db
		# self.month_n = ('январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь')

	def dbImportTypes(self):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('SELECT * FROM events')
		rawarr = curs.fetchall()
		conn.close()
		return rawarr

	def loadEvByID(self, evID, table):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('SELECT name, start, finish, members, notes FROM {} WHERE evID={}'.format(table, evID))
		res = curs.fetchone()
		conn.close()
		return TotEvents(*res) if res else None

	def storeOneEv(self, ev, month):
		'''можно переделать на авт работу'''
		mess = ''
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()

		if not self.checkTable(month):
			curs.execute('CREATE TABLE {} (name TEXT, start REAL, '
						 'finish REAL, members TEXT, notes TEXT,'
						 'evID INT PRIMARY KEY, glID TEXT)'.format(month))
			mess += f'ВНИМАНИЕ. Создана новая таблица {month} \n'


		curs.execute('INSERT INTO {} (evID, name, start, finish, members) '
					 'VALUES ({}, "{}", {}, {}, "{}")'.format(month, ev.evID, ev.name,
					 									  ev.start.timestamp(),
					 									  ev.finish.timestamp(),
					 									  ev.members))
		conn.commit()
		conn.close()
		mess += f'событие {ev.evID} {ev.name} записано в {month}\n'
		return mess

	def updateOneEv(self, ev, table):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()

		t = curs.execute('UPDATE {} SET name="{}", start={}, finish={}, members="{}" WHERE evID={}'.format(table, ev.name,
					 																				ev.start.timestamp(),
					 																				ev.finish.timestamp(),
					 																				ev.members, ev.evID))
		mess = curs.rowcount
		conn.commit()
		conn.close()
		return mess


	def loadMonth(self, month):
		'''Возвращает отсортированный список Tot Events'''
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		table_name = month
		curs.execute('SELECT name, start, finish, members FROM {}'.format(table_name))
		rawarr = curs.fetchall()
		conn.close()
		ev_arr = []
		for ev in rawarr:
			ev_arr.append(TotEvents(*ev))
		ev_arr.sort(key=self.forsort)
		return ev_arr

	def forsort(self, obj):
		return obj.start

	def checkTable(self, table):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('SELECT name FROM sqlite_master WHERE type="table"')

		temp = curs.fetchall()
		conn.close()
		temp = [n[0] for n in temp]
		return True if table in temp else False

	def getMaxId(self, table):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('SELECT MAX(evID) FROM {}'.format(table))
		res = curs.fetchone()
		conn.close()
		return res[0]

	def loadShortList(self, table):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('SELECT evID, start, name FROM {} ORDER BY start'.format(table))
		res = curs.fetchall()
		conn.close()		
		return res
