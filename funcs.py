import re
import sqlite3

dateRe = re.compile(r'([1-3]?\d) ((?:[0-1]?[0-9]|2[0-4])[0-5]\d) ((?:[1-3]?\d) )?((?:[0-1]?[0-9]|2[0-4])[0-5]\d)')

class TotEvents():
	def __init__(self, name, start, finish, members, notes = ''):
		self.evId = 0
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
		self.month_n = ('январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь')

	def dbImportTypes(self):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('SELECT * FROM events')
		rawarr = curs.fetchall()
		conn.close()
		return rawarr

	def storeOneEv(self, ev, month):
		'''можно переделать на авт работу'''
		mess = ''
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		table_name = self.month_n[int(month)-1]
		try:
			curs.execute('CREATE TABLE {} (name TEXT, start REAL, '
						 'finish REAL, members TEXT, notes TEXT,'
						 'evID INT PRIMARY KEY, glID TEXT)'.format(table_name))
		except sqlite3.OperationalError:
			mess += f'Таблица {table_name} уже есть, будет дополнена\n'
		curs.execute('INSERT INTO {} (name, start, finish, members) '
					 'VALUES ("{}", {}, {}, "{}")'.format(table_name, ev.name,
					 									  ev.start.timestamp(),
					 									  ev.finish.timestamp(),
					 									  ev.members))
		conn.commit()
		conn.close()
		mess += f'событие {ev.name} записано\n'
		return mess

	def loadMonth(self, month):
		'''Возвращает отсортированный список Tot Events'''
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		table_name = self.month_n[int(month)-1]
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