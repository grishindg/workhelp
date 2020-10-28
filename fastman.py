#Основной файл
# import sqlite3
import datetime as dt
import tkinter as tk
import locale
from tkinter import ttk

from svgwriter import SVGwriter

from funcs import TotEvents, dateRe, DBwriter, SynWithGoogle, WORKERS, EMAILS, transEv

locale.setlocale(locale.LC_TIME, "ru_RU")

PATH_TO_DB = './files/events.db'
EXFILE = './files/events.xlsx'



class Fastman(tk.Frame):
	def __init__(self, master):
		super().__init__(master)
		self.master = master

		self.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)
		# self.grid(column=0, row=0, padx=5, pady=5)
		# self.columnconfigure(0, weight=1)
		self.columnconfigure(2, weight=1)
		self.rowconfigure(2, weight=1)

		#Переменные__________________________
		
		self.vID = tk.IntVar(value=0) #внутренний id события, пока не используется
		self.lastID = 0 #Последний записанный id, перед присвоением его надо увеличить

		self.vTime = tk.StringVar()
		self.vEvent = tk.StringVar()


		self.vYear = tk.IntVar(value=2020)

		self.vNameOfMonth = tk.StringVar() #переменная для списка имен месяцев

		self.vListOfEvents = tk.StringVar() #Для Listboxа
	
		self.listNamesEvents = [] #Переменная для полного списка имен, 
		self.modyfListNamesEvents = [] #для присваивания vListOfEvents чтобы фильтровать список
									   #чтобы не вытаскивать список из строки vListOfEvents
		self.mainEventsArr = [] #Сюда скидывается список типовых событий из базы  данных

		# self.timeTable = [] # Созданное расписание
	
		self.dbWr = DBwriter(PATH_TO_DB)
		self.svgWriter = SVGwriter()

		#функции инициализации___________
		self.loadTypeEvents()
		self.create_widgets()
		print('наполнение из базы')
		

	def create_widgets(self):
		#Инициализация__________________

		self.frYrMn = tk.Frame(self)
		self.frWorkers = tk.Frame(self)

		self.lManual = tk.Label(self, anchor='nw', justify='left',
								text='F1 запись  F3 выгрузить\nF2 оч участ\nF5 обновить')
		self.eID = tk.Entry(self, width = 3, textvariable=self.vID, state='disable')

		self.eYear = tk.Entry(self.frYrMn, textvariable=self.vYear, width=4, takefocus=0)
		# self.eMonth = tk.Entry(self.frYrMn, textvariable=self.vMonth, width=4, takefocus=0)
		self.eTime = tk.Entry(self.frYrMn, width = 15, textvariable=self.vTime)
		self.eEvent = tk.Entry(self, width = 50, textvariable=self.vEvent)
		self.lWorkers = tk.Label(self, text = 'Работники')
		self.lbEvents = tk.Listbox(self, height=4, width=50, listvariable=self.vListOfEvents)
		self.cbMonth = ttk.Combobox(self.frYrMn, textvariable=self.vNameOfMonth, width=10,
								    takefocus=0, state='readonly',
									values=('январь', 'февраль', 'март', 'апрель',
											'май', 'июнь', 'июль', 'август',
											'сентябрь', 'октябрь', 'ноябрь', 'декабрь'))
		self.cbMonth.current(0)

		self.tCnsl = tk.Text(self, width=60, height=10, takefocus=0)

		self.bGsynh = tk.Button(self.frWorkers, text='Gsynh', command=self.synWithGoogle)
		self.bPrintImage = tk.Button(self.frWorkers, text='Print', command=self.saveSVG)

		self.chWorkers = []
		self.varWorkers = []
		self.lStats = []
		for i in range(len(WORKERS)):
			tempvar = tk.BooleanVar()
			tempvar.set(0)
			self.varWorkers.append(tempvar)
			tempbt = tk.Checkbutton(self.frWorkers,
									text=WORKERS[i],
									variable=tempvar,
									takefocus=0)
			tempbt.grid(row=i, column=0, sticky=tk.NW)

			self.chWorkers.append(tempbt)
			tempLb = tk.Label(self.frWorkers, text='(⌒ω⌒)', width=8, takefocus=0)
			tempLb.grid(row=i, column=1, sticky=tk.NW)
			self.lStats.append(tempLb)



		#Позиционирование________________
		self.bGsynh.grid(row=len(WORKERS)+1, column=0, sticky=tk.E)
		self.bPrintImage.grid(row=len(WORKERS)+1, column=1, sticky=tk.E)

		self.frYrMn.grid(row = 0, column = 1, sticky=tk.E)
		self.frWorkers.grid(row=1, column=3, rowspan=3, sticky=tk.NW)

		self.lManual.grid(row=1, column=0, columnspan=2, sticky=tk.W)

		self.eID.grid(row=0, column=0, sticky=tk.W)
		# self.eMonth.grid(row=0, column=1, sticky=tk.E)
		self.eYear.grid(row=0, column=0, sticky=tk.E)
		self.lbEvents.grid(row=1, column=2, sticky=tk.E)
		self.eTime.grid(row=0, column=3, sticky=tk.E)

		self.cbMonth.grid(row=0, column=1, sticky=tk.E)
		# self.lConsole.grid(row=1, column=1, sticky=tk.NE)

		self.lWorkers.grid(row=0, column=3)

		self.eEvent.grid(row=0, column=2, sticky=tk.E)

		self.tCnsl.grid(row=2, column=0, rowspan=2, columnspan=3, sticky=(tk.N, tk.S, tk.E, tk.W))



		#БИНДЫ__________________________

		self.eEvent.bind('<KeyRelease>', self.namesChange)
		self.eEvent.bind('<Down>', self.chFocusTolist)
		self.lbEvents.bind('<Return>', self.applyEvent)
		#бинды всего приложения
		self.master.bind('<F2>', self.clearWorkers)
		self.master.bind('<F1>', self.store)
		self.cbMonth.bind('<<ComboboxSelected>>', self.callCB)
		self.master.bind('<F5>', self.callCB)
		self.master.bind('<F3>', self.loadEvent) 
		# self.master.bind('<F10>', self.synWithGoogle)
		# self.master.bind('<F11>', self.getStats)
		#Функции по событиям и нет______

	def callCB(self, event):
		month = self.vNameOfMonth.get()
		if self.dbWr.checkTable(month):

			self.lastID = self.dbWr.getMaxId(month)
			self.eID['state']= 'normal'
			#вывод в консоль
			temp_arr = self.dbWr.loadShortList(month)
			temp_arr.reverse()
			self.toConsole( '-----------------------------')
			for ev in temp_arr:
				start = dt.datetime.fromtimestamp(ev[1])
				finish = dt.datetime.fromtimestamp(ev[2])
				if start.day != finish.day:
					self.toConsole( f'!! несовпадение дней начала и конца !!')
				start = start.strftime('%a%d %H%M')
				finish = finish.strftime('%H%M') #внимание ! не учитывает если мероприятие переходит на 2 день
				self.toConsole( f'{ev[0]} {start}-{finish} {ev[3]}')
			self.getStats()
			self.toConsole( '-----------------------------')
			self.toConsole( f'месяц {month} есть в базе, lastID установлен в {self.lastID}')
		else:
			self.eID['state']= 'disable'

			self.lastID = 0
			self.clearStats()
			self.toConsole( 'новый месяц, последний id установлен в 0')
		self.clear()

	def loadEvent(self, event):
		temp_id = self.vID.get()
		if not temp_id:
			self.toConsole('-- ID события на нуле --')
			return
		ev = self.dbWr.loadEvByID(temp_id, self.vNameOfMonth.get())
		if not ev:
			self.toConsole('-- Такого ID нет --')
			return

		self.vEvent.set(ev.name)

		# очищаем галочки участников, и если есть в событие, выставляем
		self.clearWorkers()
		members = ev.members.split(' ')
		if ev.members:
			for name in members:#TODO ОШИБКА!!
				self.varWorkers[WORKERS.index(name)].set(1)
		start = dt.datetime.fromtimestamp(ev.start)
		finish = dt.datetime.fromtimestamp(ev.finish)
		self.vTime.set(start.strftime('%d %H%M ') + finish.strftime('%d %H%M'))

		self.toConsole('-- событие загружено --')

	def loadTypeEvents(self):
		'''при инициализации заполняет список для Лисбокса типовых спектакль'''
		self.mainEventsArr = self.dbWr.dbImportTypes()
		self.listNamesEvents = [x[0] for x in self.mainEventsArr]
		self.vListOfEvents.set(self.listNamesEvents[:])
		self.modyfListNamesEvents = self.listNamesEvents[:]


		#События_______________________
	def store(self, event):
		'''Добавляем событие в список событий (в локальную базу), по кнопке'''
		#проверяем соответсвие времени
		overh = False #если указано 24 часа, это переменная добавит день
		time = self.eTime.get()
		traceddate = dateRe.fullmatch(time)
		if not traceddate:
			# print('НЕ ФОРМАТ ДАТЫ')
			self.toConsole( 'Неверный формат даты')
			return
		rawlist = traceddate.groups()
		secnday = rawlist[2] if rawlist[2] else rawlist[0] #если не упомянут второй день, используется первый
		if int(rawlist[3][:-2]) >= 24: #меняет 24 на 0
			overh = True 
			new_fin = '0' + rawlist[3][-2:]
			rawlist = (rawlist[0],
					   rawlist[1],
					   rawlist[2],
					   new_fin)

		start = dt.datetime(self.vYear.get(), self.cbMonth.current()+1,
							int(rawlist[0]),
							int(rawlist[1][:-2]),
							int(rawlist[1][-2:]))
		finish = dt.datetime(self.vYear.get(), self.cbMonth.current()+1,
							int(secnday),
							int(rawlist[3][:-2]),
							int(rawlist[3][-2:]))
		if overh:
			finish += dt.timedelta(days=1)
		members = ''

		for i in range(len(WORKERS)):
			if self.varWorkers[i].get():
				members += ' ' + WORKERS[i]
		members = members.strip()

		ev = TotEvents(self.vEvent.get(), start, finish, members)

		temp_id = self.vID.get()
		if not temp_id:
			#!!!!!!!!!!
			self.lastID += 1
			#!!!!!!!!!!
			ev.evID = self.lastID
			mess = self.dbWr.storeOneEv(ev, self.vNameOfMonth.get())
			self.getStats()
			self.toConsole(mess)
		else:
			ev.evID = temp_id
			mess = self.dbWr.updateOneEv(ev, self.vNameOfMonth.get())
			mess =  'Событие обновлено' if mess else '-! НЕ ОБНОВЛЕНО !-'
			self.getStats()
			self.toConsole(mess)

		self.clear()

	def toConsole(self, text):
		self.tCnsl.insert('1.0', text + '\n')

	def saveSVG(self, event=None):
		month = self.vNameOfMonth.get()
		if self.dbWr.checkTable(month):

			holydays = self.dbWr.getStats(month)[1]

			self.svgWriter.saveSvg(self.dbWr.loadMonth(month), holydays)
			self.toConsole('Изображение сохранено')

	def namesChange(self, event):
		'''редактирует список событий в момент набора (автодополнение)'''
		tempt = self.vEvent.get()
		if not tempt:
			self.vListOfEvents.set(self.listNamesEvents[:])
			self.modyfListNamesEvents = self.listNamesEvents[:]
			return
		self.modyfListNamesEvents = [ev for ev in self.listNamesEvents if ev.find(tempt) != -1]
		self.vListOfEvents.set(self.modyfListNamesEvents)

	def chFocusTolist(self, event):
		self.lbEvents.focus_set()
		self.lbEvents.selection_clear(0,tk.END)
		self.lbEvents.select_set(0)

	def applyEvent(self, event):
		'''Когда выбрано собыите, по клавише Enter заполняются данные'''
		tempind = self.lbEvents.curselection()
		if len(tempind) == 0:
			print('Ничего не выбрано')
			return
		ind = tempind[0]
		for ev in self.mainEventsArr:
			if ev[0] == self.modyfListNamesEvents[ind]:
				self.vTime.set(ev[1])
				self.vEvent.set(ev[0])
				if ev[2] and ev[2] != 'None':
					for w in ev[2].split(' '):
						temppoint = self.chWorkers[WORKERS.index(w)]
						temppoint['bg'] = 'GREY'

				break
		self.eTime.focus_set()



	def clear(self):
		'''очищает все кроме '''
		for ch in self.chWorkers:
			ch['bg'] = 'SystemButtonFace'

		self.vTime.set('')
		self.vEvent.set('')
		self.vListOfEvents.set(self.listNamesEvents[:])
		self.modyfListNamesEvents = self.listNamesEvents[:]
		self.vID.set(0)
		self.eEvent.focus_set()

	def clearWorkers(self, event=None):
		for w in self.varWorkers:
			w.set(0)

	def getStats(self, event=None):
		if not self.lastID:
			self.toConsole('-!getStats: не исполнено!-')
			return
		res = self.dbWr.getStats(self.vNameOfMonth.get())

		for st, hl, lb in zip(*res, self.lStats):
			lb['text'] = f'{st} {len(hl)}'

	def clearStats(self):
		for st in self.lStats:
			st['text'] = '(⌒ω⌒)'

	def synWithGoogle(self, event=None):
		'''функция синхронизации, делает всё'''

		mailToName = dict(zip(EMAILS, WORKERS))
		synher = SynWithGoogle(self.toConsole)
		# 1 Проверяем есть ли новые события и если есть пишем в гугл
		newEvnts = self.dbWr.getCreatedEvents(self.vNameOfMonth.get())
		self.toConsole('-- поиск новых событий в ЛБД --')
		cn = 0
		for ev in newEvnts:
			self.toConsole(f'{ev.name} {ev.evID} {ev.members}')
			glEv = synher.newEvToGl(ev)
			new_ev = ev.copy()
			new_ev.glID = glEv['id']
			new_ev.updated = glEv['updated']
			mess = self.dbWr.store_glID(new_ev, self.vNameOfMonth.get())
			self.toConsole(f'пишем {new_ev.evID} {new_ev.name} {new_ev.glID} статус - {mess}')
			cn += 1
		self.toConsole(f'-- получено {cn} новых glID --')

		# 2 Выгружаем месяц
		self.toConsole('-- выгрузка месяца из gl и локальной БД --')
		glEvents = synher.getMonth(self.vNameOfMonth.get())
		lbEvents = self.dbWr.loadMonth(self.vNameOfMonth.get())
		lbIDs = {lb_ev.glID: lb_ev for lb_ev in lbEvents} #словарь локальных событий для быстрого обращения к событию по glID
		# 3 Проверяем есть ли glID событие в локальной базе, поиск событий
		#   созданный в калнедаре
		self.toConsole('-- поиск событий созданных в G календаре --')
		for glEv in glEvents:
			if glEv['id'] not in lbIDs:
				self.toConsole(f"--!! событие {glEv['summary']} создано в G календаре !!--")

		# 3.1 Пишем событие в ЛБЗ #TODO перевести в функцию transEv

				new_ev = transEv(glEv, evID = self.lastID+1)

				self.dbWr.storeOneEv(new_ev, self.vNameOfMonth.get())

				self.lastID+=1
				self.toConsole(f'событие {new_ev.name} записано в ЛБЗ c id {new_ev.evID}')
		# 4 сравниваем update
			else:
				self.toConsole(f"-- событие {glEv['summary']} есть в лб --")
				# self.toConsole('сравниваем updated')
				t_ldb = dt.datetime.fromisoformat( lbIDs[glEv['id']].updated[:-1] )
				t_gldb = dt.datetime.fromisoformat( glEv['updated'][:-1] )

				if t_gldb == t_ldb:
					# self.toConsole(f"события {glEv['summary']} одинаковы")
					continue
				elif t_gldb > t_ldb:
					self.toConsole(f"--! событие {glEv['summary']} было обновлено в G календаре !--")
					upd_ev = transEv(glEv, evID = lbIDs[glEv['id']].evID)
					self.dbWr.updateOneEv(upd_ev, self.vNameOfMonth.get(), fromGcal=True)

					self.toConsole(f'событие {upd_ev.evID} {upd_ev.name} обновлено в лб из G кал')
					# использовать функцию перевода объекта из gl в lb
					# обновить lb
					# transEv(glEv)


				elif t_gldb < t_ldb:
					self.toConsole(f"--! событие {glEv['summary']} в было обновлено локально !--")
					new_ev = transEv(lbIDs[glEv['id']], mode='LtoG')

					status = synher.updateOneEv(new_ev, glEv['id']) 
					if not status:
						self.toConsole('!!! не удалось прообдейтить в G кал !!!')
						return
					new_updated = status['updated']
					self.toConsole(f'новое время апдейта от гугл {new_updated}')
					mess = self.dbWr.updateUpdated(lbIDs[glEv['id']].evID, new_updated, self.vNameOfMonth.get())
					self.toConsole(f'--! и update обновлен локально. статус - {mess} !--')
					self.toConsole('--! Событие измененное локально, обновлено в G кал !--')
					# использовать функцию перевода из lb d gl
					# обновить gl


		self.toConsole('-------------')
		self.toConsole('-- синхронизация завершена --')







def main():
	root  = tk.Tk()	
	root.title('Расписание')
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)
	fastapp = Fastman(root)
	fastapp.mainloop()


if __name__ == '__main__':
	main()