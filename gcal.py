#работаем с google cal

from __future__ import print_function
import datetime as dt
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request





def getGservice():
	SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
		  	  'https://www.googleapis.com/auth/calendar.events']

	tempEvBody = {'summary': '',
			   'start': {'dateTime': ''},
			   'end': {'dateTime': ''},
			   'attendees': [{'email': '',},]
			   }

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

	# return service

	tzi = dt.timezone(dt.timedelta(hours=3))
	hr = dt.timedelta(hours=1)
	startdt = dt.datetime(year=2020, month=9, day=12, hour=12, tzinfo=tzi)
	finishdt = startdt + hr







	totid = '3b30rdt7apium4ruf2bt4st2jo@group.calendar.google.com'

	# event = service.events().insert(calendarId=totid, body=body_ev).execute()
	testEvent='c125s76m33a2c7irf2rfqkm5jk'
	# event = service.events().get(calendarId=totid, eventId=testEvent).execute()
	month_n = ('январь', 'февраль', 'март', 'апрель',
				'май', 'июнь', 'июль', 'август',
				'сентябрь', 'октябрь', 'ноябрь', 'декабрь')
	month = 'ноябрь'
	tmin = dt.datetime(2020, month_n.index(month)+1, 1, tzinfo=tzi)
	tmax = dt.datetime(2020, month_n.index(month)+2, 1, tzinfo=tzi)
	events = service.events().list(calendarId=totid, showDeleted=False,
								   timeMin = tmin.isoformat(timespec='seconds'),
								   timeMax = tmax.isoformat(timespec='seconds')).execute()
	# print(events.keys())

	# for event in events['items']:
	# 	print(event)
		# print(event['summary'])
		# print(event['description'])

	for event in events['items']:
		service.events().delete(calendarId=totid, eventId=event['id']).execute()
		# print(event['summary'])
		# print(event['description'])





if __name__ == '__main__':
	getGservice()
	# pass