import re
import sqlite3
dateRe = re.compile(r'([1-3]?\d) ((?:[0-1]?[0-9]|2[0-4])[0-5]\d) ((?:[1-3]?\d) )?((?:[0-1]?[0-9]|2[0-4])[0-5]\d)')

class TotEvents():
	def __init__(self, name, start, finish, members, notes = ''):
		self.name = name
		self.start = start
		self.finish = finish
		self.members = members
		self.notes = notes

class DBwriter():
	'''класс для работы с базой данных'''
	def __init__(self, MF, db):
		self.db = db
		self.MF = MF

	def db_import(self):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('SELECT * FROM events')
		self.MF.mainEventsArr = curs.fetchall()
		conn.close()
		self.MF.listNamesEvents = [x[0] for x in self.MF.mainEventsArr]
		self.MF.vListOfEvents.set(self.MF.listNamesEvents[:])
		self.MF.modyfListNamesEvents = self.MF.listNamesEvents[:]

	def storeTTinDb(self):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		table_name = self.MF.month_n[int(self.MF.vMonth.get()-1)]
		try:
			curs.execute('CREATE TABLE {} (name TEXT, start REAL, finish REAL, members TEXT, notes TEXT)'.format(table_name))
		except sqlite3.OperationalError:
			print(f'Таблица {table_name} уже есть, будет дополнена')
			# curs.execute('DELETE FROM {}'.format(table))
		for ev in self.MF.timeTable:
			curs.execute('INSERT INTO {} VALUES ("{}", {}, {}, "{}", "{}")'.format(table_name, ev.name, ev.start.timestamp(), \
																				   ev.finish.timestamp(), ev.members, ev.notes))
		conn.commit()
		conn.close()
		print('Записано')