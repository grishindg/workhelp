import re
import sqlite3
import datetime as dt
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

dateRe = re.compile(r'([0-3]?\d) ((?:[0-1]?[0-9]|2[0-4])[0-5]\d) ((?:[0-3]?\d) )?((?:[0-1]?[0-9]|2[0-4])[0-5]\d)')
WORKERS = ('Даниил', 'Влад', 'Андрей', 'Марина', 'Арсений', 'Ольга', 'Василий','Денис')
EMAILS = ('danja21dedkov@gmail.com',
		  'hirurg3000@mail.ru',
		  'andryukha1999.mitin@gmail.com',
		  'mkopylova885@gmail.com',
		  'arsenij-rad@mail.ru',
		  'syrovatchenkoov@gmail.com',
		  'ixofun@gmail.com',
		  'grishindg@gmail.com')


class TotEvents:
	def __init__(self, name, start, finish, members = '', notes = '', evID = 0, glID = '', updated = ''):

		self.name = name
		self.start = start
		self.finish = finish
		self.members = members
		self.notes = notes
		self.evID = evID
		self.glID = glID
		self.updated = updated

	def __str__(self):
		mess = 'TotEvent: ('
		for i in self.__dict__.keys():
			if self.__dict__[i]: mess = mess + str(self.__dict__[i]) + ' '
		return mess + ')'

	def copy(self):
		return TotEvents(self.name, self.start, self.finish,
						 self.members, self.notes, self.evID,
						 self.glID, self.updated)


class DBwriter:
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
		#ОЖИДАЕТ ВРЕМЯ В ФОРМАТЕ DATETIME
		mess = ''
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()

		if not self.checkTable(month):
			curs.execute('CREATE TABLE {} (name TEXT, start REAL, '
						 'finish REAL, members TEXT, notes TEXT,'
						 'evID INT PRIMARY KEY, glID TEXT, updated TEXT)'.format(month))
			mess += f'ВНИМАНИЕ. Создана новая таблица {month} \n'


		curs.execute('INSERT INTO {} '
					 'VALUES ("{}", {}, {}, "{}", "{}", "{}", "{}", "{}")'.format(month, ev.name,
														  ev.start.timestamp(),
														  ev.finish.timestamp(),
														  ev.members,
														  ev.notes,
														  ev.evID,
														  ev.glID,
														  ev.updated))
		conn.commit()
		conn.close()
		mess += f'событие {ev.evID} {ev.name} записано в {month}'
		return mess

	def updateOneEv(self, ev, table, fromGcal=False):#TODO сделать запись update c связи с google
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()

		if not fromGcal: 
			# локальное обновление не меняет gl id если он есть
			updated = dt.datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
			curs.execute('UPDATE {} SET name="{}", start={}, finish={}, members="{}", notes="{}", updated="{}" WHERE evID={}'.format(table, ev.name,
																										   ev.start.timestamp(),
																										   ev.finish.timestamp(),
																										   ev.members, ev.notes,
																										   updated,
																										   ev.evID))
		else:
			# Не меняется gl id, и lb id
			print('применяется обновление из гугл')
			curs.execute('UPDATE {} SET name="{}", start={}, finish={}, '
						 'members="{}", notes="{}", updated = "{}" WHERE evID={}'.format(table, ev.name,
																						 ev.start.timestamp(),
																						 ev.finish.timestamp(),
																						 ev.members,
																						 ev.notes,
																						 ev.updated,
																						 ev.evID))

		mess = curs.rowcount
		conn.commit()
		conn.close()
		return mess

	def updateUpdated(self, evID, updated, table):
		'''меняет updated изменненного ранее в лб события для для точного соответсвия с g кал'''
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('UPDATE {} SET updated="{}" WHERE evID={}'.format(table, updated, evID))
		mess = curs.rowcount
		conn.commit()
		conn.close()
		return mess

	def store_glID(self, ev, table):
		'''добавляет glID и updated в локальную базу после загрузки в гугл''' 
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('UPDATE {} SET glID = "{}", updated="{}" WHERE evID={}'.format(table, ev.glID, ev.updated, ev.evID))
		mess = curs.rowcount
		conn.commit()
		conn.close()
		return mess

	def loadMonth(self, month):
		'''Возвращает отсортированный список Tot Events'''
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		table_name = month
		curs.execute('SELECT * FROM {}'.format(table_name))
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

	def loadShortList(self, table): #TODO возвращать TOT event?
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('SELECT evID, start, finish, name FROM {} ORDER BY start'.format(table))
		res = curs.fetchall()
		conn.close()		
		return res

	def getCreatedEvents(self, table):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()
		curs.execute('SELECT name, start, finish, members, notes, evID '
					 'FROM {} WHERE glID = "" OR glID IS NULL'.format(table))
		rawarr = curs.fetchall()
		conn.close()		
		res = []
		for ev in rawarr:
			res.append(TotEvents(*ev))
		return res

	def getStats(self, table):
		conn = sqlite3.connect(self.db)
		curs = conn.cursor()		
		curs.execute('SELECT start, finish, members FROM {} ORDER BY start'.format(table))
		res = curs.fetchall()
		conn.close()

		stat = []
		holidays = []

		firstday = dt.datetime.fromtimestamp(res[0][0]).day
		lastday = dt.datetime.fromtimestamp(res[-1][0]).day


		for name in WORKERS:
			days = list(range(firstday,lastday+1))
			hours = 0
			for ev in res:
				if name not in ev[2].split(' '):
					continue
				hours += (ev[1] - ev[0])/3600
				day = dt.datetime.fromtimestamp(ev[0])
				if day.day in days:
					days.remove(day.day)
			stat.append(hours)
			holidays.append(days)

		return (stat, holidays)
class SynWithGoogle:
	def __init__(self, toConsole):
		self.month_n = ('январь', 'февраль', 'март', 'апрель',
						'май', 'июнь', 'июль', 'август',
						'сентябрь', 'октябрь', 'ноябрь', 'декабрь')
		self.tzi = dt.timezone(dt.timedelta(hours=3))
		self.toConsole = toConsole
		self.service = self.getGservice()
		self.tempEvBody = {'summary': '',
						   'start': {'dateTime': ''},
						   'end': {'dateTime': ''},
						   'attendees': [],
						   'reminders':{'useDefault':False}
						   }
		self.totid = '3b30rdt7apium4ruf2bt4st2jo@group.calendar.google.com'
		self.nameToMail = dict(zip(WORKERS, EMAILS))

	@staticmethod
	def getGservice():
		'''возвращает указатель на service'''
		SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
				  'https://www.googleapis.com/auth/calendar.events']
				  
		"""Shows basic usage of the Google Calendar API.
		Prints the start and name of the next 10 events on the user's calendar.
		"""
		creds = None
		# The file token.pickle stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists('./files/token.pickle'):
			print('файл токена есть')
			with open('./files/token.pickle', 'rb') as token:
				creds = pickle.load(token)
		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				print('файл токена есть, но истек')
				creds.refresh(Request())
			else:
				print('файла токена нет или не подходит, делаем новый с помощью credentials.json')
				flow = InstalledAppFlow.from_client_secrets_file(
					'./files/credentials.json', SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open('./files/token.pickle', 'wb') as token:
				pickle.dump(creds, token)

		service = build('calendar', 'v3', credentials=creds)
		print('-- Создан service объект --')
		return service

	def newEvToGl(self, ev):
		'''добавляет событие в ggl календарь, возвращает заполненный объект'''
		body = {'summary': '',
				'start': {'dateTime': ''},
				'end': {'dateTime': ''},
				'attendees': [],
				'reminders':{'useDefault':False}
				}
		body['summary'] = ev.name
		start = dt.datetime.fromtimestamp(ev.start, tz = self.tzi)
		finish = dt.datetime.fromtimestamp(ev.finish, tz = self.tzi)
		body['start']['dateTime'] = start.isoformat(timespec='seconds')
		body['end']['dateTime'] = finish.isoformat(timespec='seconds')
		if ev.notes:
			body.update({'description':ev.notes})
		if ev.members:
			for i in ev.members.split(' '):
				body['attendees'].append({'email':self.nameToMail[i]})

		event = self.service.events().insert(calendarId=self.totid, body=body).execute()
		self.toConsole('-- новое событие добавлено в ggl --')
		return event

	def updateOneEv(self, ev, glID):# можно переделать под внутреннее использование
		return self.service.events().update(calendarId=self.totid, eventId=glID, body=ev).execute()

	def getMonth(self, month): #TODO сделать год
		tmin = dt.datetime(2021, self.month_n.index(month)+1, 1, tzinfo=self.tzi)
		tmax = dt.datetime(2021, self.month_n.index(month)+2, 1, tzinfo=self.tzi) + dt.timedelta(seconds=1)
		events = self.service.events().list(calendarId=self.totid,
											timeMin = tmin.isoformat(timespec='seconds'),
											timeMax = tmax.isoformat(timespec='seconds')).execute()
		return events['items']


def transEv(event, mode='GtoL', evID=0):
	'''перевод типособытия'''
	tempEvBody = {'summary': '',
				   'start': {'dateTime': ''},
				   'end': {'dateTime': ''},
				   'attendees': [], #TODO проверить notes??
				 }
	mailToName = dict(zip(EMAILS, WORKERS))
	nameToMail = dict(zip(WORKERS, EMAILS))

	if mode == 'GtoL' and evID:

		members = []
		description = ''
		if 'description' in event:
			description = event['description']
		if 'attendees' in event:
			for em in event['attendees']:
				members.append(mailToName[em['email']])

		new_ev = TotEvents(event['summary'],
						   dt.datetime.fromisoformat(event['start']['dateTime']),
						   dt.datetime.fromisoformat(event['end']['dateTime']),
						   ' '.join(members),
						   description,
						   evID, # строго необходимо указать
						   event['id'],
						   event['updated']
						   )
		return new_ev

	elif mode == 'LtoG' and not evID:

		tzi = dt.timezone(dt.timedelta(hours=3))
		body = tempEvBody.copy()
		body.update({'sendUpdates':'none'})
		body['summary'] = event.name
		start = dt.datetime.fromtimestamp(event.start, tz = tzi)
		finish = dt.datetime.fromtimestamp(event.finish, tz = tzi)
		body['start']['dateTime'] = start.isoformat(timespec='seconds')
		body['end']['dateTime'] = finish.isoformat(timespec='seconds')
		if event.notes:
			body.update({'description':event.notes})
		if event.members:
			for i in event.members.split(' '):
				body['attendees'].append({'email':nameToMail[i]})

		return body

	else:
		return None
