#Основной файл
import sqlite3
import datetime as dt
import tkinter as tk
from tkinter import ttk

from funcs import TotEvents, dateRe
from openpyxl import load_workbook


PATH_TO_DB = './files/events.db'
EXFILE = './files/events.xlsx'
WORKERS = ['Даниил', 'Влад', 'Андрей', 'Марина', 'Арсений', 'Ольга', 'Василий','Денис']

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

		self.vYear = tk.IntVar(value=2020)
		self.vMonth = tk.IntVar(value=8)
	
		self.vListOfEvents = tk.StringVar() #Для Listboxа
	
		self.listNamesEvents = [] #Переменная для полного списка имен, 
		self.modyfListNamesEvents = [] #для присваивания vListOfEvents чтобы фильтровать список
									   #чтобы не вытаскивать список из строки vListOfEvents
		self.mainEventsArr = [] #Сюда скидывается список типовых событий из базы из базы данных
		self.timetTable = [] # Созданное расписание

		self.create_widgets()
		print('наполнение из базы')
		self.db_import(PATH_TO_DB)

	def create_widgets(self):
		#Инициализация__________________

		self.bNewEvent = tk.Button(self, text = 'Ебаш', command=self.store)
		# self.lStart = tk.Label(self, text = 'время')
		self.eYear = tk.Entry(self, textvariable=self.vYear, width=4, takefocus=0)
		self.eMonth = tk.Entry(self, textvariable=self.vMonth, width=4, takefocus=0)
		self.eTime = tk.Entry(self, textvariable=self.vTime)
		self.eEvent = tk.Entry(self, width = 50, textvariable=self.vEvent)
		self.lWorkers = tk.Label(self, text = 'Работники')
		self.lbEvents = tk.Listbox(self, height=4, width=50, listvariable=self.vListOfEvents)
		self.frWorkers = tk.Frame(self)
		self.somech = tk.Checkbutton(self.frWorkers, text='some')

		self.tPole = tk.Text(self, width=80)

		#Позиционирование________________

		self.bNewEvent.grid(row = 0, column = 0, padx=5, pady=5, sticky=tk.W)
		self.eMonth.grid(row=0, column=0, sticky=tk.E)
		self.eYear.grid(row=1, column=0, sticky=tk.NE)
		self.lbEvents.grid(row=1, column=2)
		self.eTime.grid(row=0, column=1, sticky=tk.E)

		self.lWorkers.grid(row=0, column=3)

		self.eEvent.grid(row=0, column=2)
		self.frWorkers.grid(row=1, column=3, rowspan=3, sticky=tk.NW)
		self.tPole.grid(row=2, column=0, rowspan=2, columnspan=3)

		self.chWorkers = []
		self.varWorkers = []
		for i in range(len(WORKERS)):
			tempvar = tk.BooleanVar()
			tempvar.set(0)
			self.varWorkers.append(tempvar)
			tempbt = tk.Checkbutton(self.frWorkers,
									text=WORKERS[i],
									variable=tempvar)
			tempbt.grid(row=i, column=0, sticky=tk.NW)
			self.chWorkers.append(tempbt)
			# self.chWorkers[0]['bg'] = 'GREY'
			# self.chWorkers[0]['bg'] = 'SystemButtonFace'
		#БИНДЫ__________________________

		self.eEvent.bind('<KeyRelease>', self.namesChange)
		self.eEvent.bind('<Down>', self.chFocusTolist)
		self.lbEvents.bind('<Return>', self.applyEvent)


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

		#События_______________________
	def store(self):
		#проверяем соответсвие времени
		overh = False
		time = self.eTime.get()
		traceddate = dateRe.fullmatch(time)
		if not traceddate:
			print('НЕ ФОРМАТ ДАТЫ')
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
		print(self.vEvent.get())
		print(start.isoformat(sep=' '))
		print(finish.isoformat(sep=' '))
		print(members.strip())
		'''функция по нажатию Ебаш'''
		# tempstr = f'{self.vTime.get()} {self.vEvent.get()}'

		#TODO Сразу сохранять в большой лист а из нео печатать
		# self.textpos += 1
		# tempstr += '\n'
		# self.tPole.insert(f'{self.textpos}.0', tempstr)

		self.clear()

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
		for v in self.varWorkers:
			v.set(0)
		self.vTime.set('')
		self.vEvent.set('')
		self.vListOfEvents.set(self.listNamesEvents[:])
		self.modyfListNamesEvents = self.listNamesEvents[:]
		self.eEvent.focus_set()


def main():
	root  = tk.Tk()	
	root.title('Расписание')
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)
	fastapp = Fastman(root)
	fastapp.mainloop()


if __name__ == '__main__':
	main()