#Основной файл
# import sqlite3
import datetime as dt
import tkinter as tk
import locale
from tkinter import ttk

from svgwriter import SVGwriter

from funcs import TotEvents, dateRe, DBwriter

locale.setlocale(locale.LC_TIME, "ru_RU")

PATH_TO_DB = './files/events.db'
EXFILE = './files/events.xlsx'

WORKERS = ('Даниил', 'Влад', 'Андрей', 'Марина', 'Арсений', 'Ольга', 'Василий','Денис')

class Fastman(tk.Frame):
	def __init__(self, master):
		super().__init__(master)
		self.master = master

		self.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)
		# self.grid(column=0, row=0, padx=5, pady=5)
		# self.columnconfigure(0, weight=1)
		self.columnconfigure(2, weight=1)

		#Переменные__________________________
		
		self.vId = tk.IntVar(value=0) #внутренний id события, пока не используется
		self.maxId = 0

		self.vTime = tk.StringVar()
		self.vEvent = tk.StringVar()
		# self.vConsole = tk.StringVar()

		self.vYear = tk.IntVar(value=2020)
		self.vMonth = tk.IntVar(value=8)
	
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
								text='F1 запись\nF2 оч участ')
		self.eId = tk.Entry(self, width = 3, textvariable=self.vId)

		self.eYear = tk.Entry(self.frYrMn, textvariable=self.vYear, width=4, takefocus=0)
		self.eMonth = tk.Entry(self.frYrMn, textvariable=self.vMonth, width=4, takefocus=0)
		self.eTime = tk.Entry(self.frYrMn, width = 12, textvariable=self.vTime)
		self.eEvent = tk.Entry(self, width = 50, textvariable=self.vEvent)
		self.lWorkers = tk.Label(self, text = 'Работники')
		self.lbEvents = tk.Listbox(self, height=4, width=50, listvariable=self.vListOfEvents)
		
		self.tCnsl = tk.Text(self, width=60, height=10, takefocus=0)

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
		self.frYrMn.grid(row = 0, column = 1, sticky=tk.E)
		self.frWorkers.grid(row=1, column=3, rowspan=3, sticky=tk.NW)

		self.lManual.grid(row=1, column=0, sticky=tk.W)

		self.eId.grid(row=0, column=0, sticky=tk.W)
		self.eMonth.grid(row=0, column=1, sticky=tk.E)
		self.eYear.grid(row=0, column=0, sticky=tk.E)
		self.lbEvents.grid(row=1, column=2, sticky=tk.E)
		self.eTime.grid(row=0, column=3, sticky=tk.E)
		# self.lConsole.grid(row=1, column=1, sticky=tk.NE)

		self.lWorkers.grid(row=0, column=3)

		self.eEvent.grid(row=0, column=2, sticky=tk.E)

		self.tCnsl.grid(row=2, column=0, rowspan=2, columnspan=3, sticky=tk.W+tk.E)



		#БИНДЫ__________________________

		self.eEvent.bind('<KeyRelease>', self.namesChange)
		self.eEvent.bind('<Down>', self.chFocusTolist)
		self.lbEvents.bind('<Return>', self.applyEvent)
		#бинды всего приложения
		self.master.bind('<F2>', self.clearWorkers)
		self.master.bind('<F1>', self.store)
		# self.master.bind('<F3>', self.storeTTinDb)#пишем в базу данных
		#функции по событиям__________________

	def loadTypeEvents(self):
		self.mainEventsArr = self.dbWr.dbImportTypes()
		self.listNamesEvents = [x[0] for x in self.mainEventsArr]
		self.vListOfEvents.set(self.listNamesEvents[:])
		self.modyfListNamesEvents = self.listNamesEvents[:]


	def storeTTinDb(self, event):
		self.dbWr.storeTTinDb()
		'''Запись месяца в базу данных'''

		#События_______________________
	def store(self, event):#None помогает разделить функционал между кнопкой и командой
		'''Добавляем событие в список событий, по кнопке'''
		#проверяем соответсвие времени
		overh = False #если указано 24 часа, это переменная добавит день
		time = self.eTime.get()
		traceddate = dateRe.fullmatch(time)
		if not traceddate:
			# print('НЕ ФОРМАТ ДАТЫ')
			self.tCnsl.insert('1.0', 'Неверный формат даты\n')
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
		ev = TotEvents(self.vEvent.get(), start, finish, members)
		mess = self.dbWr.storeOneEv(ev, self.vMonth.get())


		self.tCnsl.insert('1.0', mess)

		self.svgWriter.saveSvg(self.dbWr.loadMonth(self.vMonth.get()))
		self.clear()

	def redrawtext(self):
		'''Вывод в окно программы списка из tableText'''
		self.tCnsl.delete('1.0', 'end')
		tfrm = r'%a %d %H:%M'
		r = 1
		for ev in self.timeTable:
			self.tCnsl.insert(f'{r}.0', f'({r}) {ev.start.strftime(tfrm)} '
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
		# self.vConsole.set('')
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