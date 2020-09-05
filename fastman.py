#Основной файл
import sqlite3
import datetime as dt
import tkinter as tk
from tkinter import ttk

from funcs import TotEvents, dateRe
from openpyxl import load_workbook

#Времмено 
# import locale
# print(locale.getlocale())
#

PATH_TO_DB = './files/events.db'
EXFILE = './files/events.xlsx'
MONTH_N = ('январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь')
WORKERS = ('Даниил', 'Влад', 'Андрей', 'Марина', 'Арсений', 'Ольга', 'Василий','Денис')

class Fastman(tk.Frame):
	def __init__(self, master):
		super().__init__(master)
		self.master = master
		# self['bg'] = 'RED'

		self.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)

		#Переменные__________________________
		self.textpos = 0 #номер строки
		self.vTime = tk.StringVar()
		self.vEvent = tk.StringVar()
		self.vConsole = tk.StringVar()

		self.vYear = tk.IntVar(value=2020)
		self.vMonth = tk.IntVar(value=8)
	
		self.vListOfEvents = tk.StringVar() #Для Listboxа
	
		self.listNamesEvents = [] #Переменная для полного списка имен, 
		self.modyfListNamesEvents = [] #для присваивания vListOfEvents чтобы фильтровать список
									   #чтобы не вытаскивать список из строки vListOfEvents
		self.mainEventsArr = [] #Сюда скидывается список типовых событий из базы из базы данных
		self.timeTable = [] # Созданное расписание

		self.create_widgets()
		print('наполнение из базы')
		self.db_import(PATH_TO_DB)

	def create_widgets(self):
		#Инициализация__________________

		self.bNewEvent = tk.Button(self, text = 'Ебаш', command=self.store)
		self.eYear = tk.Entry(self, textvariable=self.vYear, width=4, takefocus=0)
		self.eMonth = tk.Entry(self, textvariable=self.vMonth, width=4, takefocus=0)
		self.eTime = tk.Entry(self, textvariable=self.vTime)
		self.eEvent = tk.Entry(self, width = 50, textvariable=self.vEvent)
		self.lWorkers = tk.Label(self, text = 'Работники')
		self.lbEvents = tk.Listbox(self, height=4, width=50, listvariable=self.vListOfEvents)
		self.frWorkers = tk.Frame(self)
		# self.somech = tk.Checkbutton(self.frWorkers, text='some')
		self.lConsole = tk.Label(self, textvariable=self.vConsole)
		self.tPole = tk.Text(self, width=80, takefocus=0)

		self.chWorkers = []
		self.varWorkers = []
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

		#Позиционирование________________

		self.bNewEvent.grid(row = 0, column = 0, padx=5, pady=5, sticky=tk.W)
		self.eMonth.grid(row=0, column=0, sticky=tk.E)
		self.eYear.grid(row=1, column=0, sticky=tk.NE)
		self.lbEvents.grid(row=1, column=2)
		self.eTime.grid(row=0, column=1, sticky=tk.E)
		self.lConsole.grid(row=1, column=1, sticky=tk.NE)

		self.lWorkers.grid(row=0, column=3)

		self.eEvent.grid(row=0, column=2)
		self.frWorkers.grid(row=1, column=3, rowspan=3, sticky=tk.NW)
		self.tPole.grid(row=2, column=0, rowspan=2, columnspan=3)



		#БИНДЫ__________________________

		self.eEvent.bind('<KeyRelease>', self.namesChange)
		self.eEvent.bind('<Down>', self.chFocusTolist)
		self.lbEvents.bind('<Return>', self.applyEvent)
		#бинды всего приложения
		self.master.bind('<F2>', self.clearWorkers)
		self.master.bind('<F1>', self.store)
		self.master.bind('<F3>', self.storeDb)#пишем в базу данных
		#функции по событиям__________________
	def db_import(self, db):
		"""Запускается при иниц, заполняет внутр список знач из базы"""
		conn = sqlite3.connect(db)
		curs = conn.cursor()
		curs.execute('SELECT * FROM events')
		self.mainEventsArr = curs.fetchall()
		conn.close()
		self.listNamesEvents = [x[0] for x in self.mainEventsArr]
		self.vListOfEvents.set(self.listNamesEvents[:])
		self.modyfListNamesEvents = self.listNamesEvents[:] #Должен быть копией, чтобы индексы соответсвовали

	def storeDb(self, re=True):
		'''Запись месяца в базу данных'''
		conn = sqlite3.connect(PATH_TO_DB)
		curs = conn.cursor()
		table = MONTH_N[int(self.vMonth.get()-1)]
		try:
			curs.execute('CREATE TABLE {} (name TEXT, start REAL, finish REAL, members TEXT, notes TEXT)'.format(table))
		except sqlite3.OperationalError:
			print(f'Таблица {table} уже есть, будет очищена')
			curs.execute('DELETE FROM {}'.format(table))
		for ev in self.timeTable:
			curs.execute('INSERT INTO {} VALUES ("{}", {}, {}, "{}", "{}")'.format(table, ev.name, ev.start.timestamp(), \
																				   ev.finish.timestamp(), ev.members, ev.notes))
		conn.commit()
		conn.close()
		print('Записано')


		#События_______________________
	def store(self, event=None):#None помогает разделить функционал между кнопкой и командой
		'''Добавляем событие в список событий, по кнопке'''
		#проверяем соответсвие времени
		overh = False
		time = self.eTime.get()
		traceddate = dateRe.fullmatch(time)
		if not traceddate:
			# print('НЕ ФОРМАТ ДАТЫ')
			self.vConsole.set('Неверный формат даты')
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

		start = dt.datetime(self.vYear.get(), self.vMonth.get(),
							int(rawlist[0]),
							int(rawlist[1][:-2]),
							int(rawlist[1][-2:]))
		finish = dt.datetime(self.vYear.get(), self.vMonth.get(),
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

		self.timeTable.append(TotEvents(self.vEvent.get(), start, finish, members))
		self.redrawtext()
		self.clear()

	def redrawtext(self):
		'''Вывод в окно программы списка из tableText'''
		self.tPole.delete('1.0', 'end')
		tfrm = r'%a%d %H:%M'
		r = 1
		for ev in self.timeTable:
			self.tPole.insert(f'{r}.0', f'({r}) {ev.start.strftime(tfrm)} '
			 							f'{ev.finish.strftime(tfrm)} "{ev.name}" {ev.members}\n')
			r+=1

	def namesChange(self, event):
		'''редактирует список событий'''
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
		'''Когда выбано собыите, по клавише Enter заполняются данные'''
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
		for ch in self.chWorkers:
			ch['bg'] = 'SystemButtonFace'

		self.vTime.set('')
		self.vEvent.set('')
		self.vListOfEvents.set(self.listNamesEvents[:])
		self.modyfListNamesEvents = self.listNamesEvents[:]
		self.vConsole.set('')
		self.eEvent.focus_set()

	def clearWorkers(self, event):
		for w in self.varWorkers:
			w.set(0)

def main():
	root  = tk.Tk()	
	root.title('Расписание')
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)
	fastapp = Fastman(root)
	fastapp.mainloop()


if __name__ == '__main__':
	main()