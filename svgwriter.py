#Создаем графику календаря

import xml.etree.ElementTree as ET
import datetime as dt
import sqlite3
import locale
from funcs import TotEvents

PATH_TO_DB = './files/events.db'

def forsort(obj):
	return obj.start

def db_loader(db, month):
	'''возвращает отсортированный список событий TotEvents'''
	conn = sqlite3.connect(db)
	curs = conn.cursor()
	curs.execute('SELECT * FROM {}'.format(month))
	rawarr = curs.fetchall()
	conn.close()
	ev_arr = []
	for ev in rawarr:
		ev_arr.append(TotEvents(*ev))
	ev_arr.sort(key=forsort)
	return ev_arr


class SVGbuilder():
	def __init__(self, ev_arr):
		self.root = ET.Element('svg', {'xmlns': r'http://www.w3.org/2000/svg', 'viewBox': '0 0 800 500'})

		self.workers = ('Даниил', 'Влад', 'Андрей', 'Марина', 'Арсений', 'Ольга', 'Василий', 'Денис')
		self.colmns = tuple((str(i) for i in range(203, 803, 75)))
		self.leftline = '30'
		self.ev_name_x = '114'

		self.ev_w = '167'
		self.ev_h = '40'


		self.vb_width = '800'
		self.vb_height = 20

		self.ev_arr = ev_arr #отсортированный лист событий TotEvents

		self.stdBzAttrs = {'width': '74', 'height': self.ev_h, 'rx': '5', 'ry': '5', 'fill': '#505EE2'}
		self.stdEvAttrs = {'x': self.leftline, 'width': self.ev_w, 'height': self.ev_h, 'rx': '5', 'ry': '5', 'stroke': '#505EE2', 'fill': 'None'}
		self.stdTxAttrs = {'font-size': '9', 'text-anchor': 'middle', 'font-family': 'sans-serif', 'fill': '#505EE2'}

	def made_events(self):

		locale.setlocale(locale.LC_TIME, "ru_RU")
		tm_fr = r'%H:%M'


		#отрисовка имен
		for name, x in zip(self.workers, self.colmns):
			attr = {'x': str(int(x)+37), 'y': '18.5', 'fill': '#505EE2'}
			attr.update(self.stdTxAttrs)
			n = ET.SubElement(self.root, 'text', attr)
			n.text = name

		d = 0

		y = 27
		for ev in self.ev_arr:

			start = dt.datetime.fromtimestamp(ev.start)
			finish = dt.datetime.fromtimestamp(ev.finish)


			#отрисовка квадрата события
			attr = self.stdEvAttrs.copy()
			attr.update({'y': str(y)})
			ET.SubElement(self.root, 'rect', attr)
			#Имя события
			attr = self.stdTxAttrs.copy()
			attr.update({'x': self.ev_name_x, 'y': str(y+25), 'font-size': '11'})
			sbnm = ET.SubElement(self.root, 'text', attr)
			sbnm.text = ev.name
			#время начала
			attr.update({'x': '194', 'y': str(y+10), 'font-size': '9', 'text-anchor': 'end'})
			sbst = ET.SubElement(self.root, 'text', attr)
			sbst.text = start.strftime(tm_fr)
			#время конца
			attr.update({'y': str(y+35)})
			sbfn = ET.SubElement(self.root, 'text', attr)
			sbfn.text = finish.strftime(tm_fr)

			if d < start.day:
				attr = self.stdTxAttrs.copy()
				attr.update({'x': '28', 'y': str(y+10), 'text-anchor': 'end'})
				day_label = ET.SubElement(self.root, 'text', attr)
				day_label.text = start.strftime('%a %d')
				d = start.day
				self.drawline(y, True)
			else:
				self.drawline(y)		



			members = ev.members.split(' ')
			
			for w in members:
				if not w:
					continue
				self.drawBzBox(self.workers.index(w), y)


			y += 42

		self.root.attrib.update({'viewBox': f'0 0 800 {y+40}'})
		tree = ET.ElementTree(self.root)
		tree.write('./files/image.svg', encoding="utf-8")
		print('Изображение сохранено ')

	def drawline(self, y, day=False):
		attr = {'x1': '200', 'x2': '798', 'y1': str(y-1), 'y2': str(y-1), 'stroke': '#AAAAAA', 'fill': 'None', 'stroke-width': '0.5'}
		if day:
			attr.update({'stroke-width': '1', 'stroke': '#505EE2'})
		ET.SubElement(self.root, 'line', attr)

	def drawBzBox(self, index, y):
		'''рисует бокс занятости'''
		attr = {'y': str(y), 'x': self.colmns[index]}
		attr.update(self.stdBzAttrs)
		ET.SubElement(self.root, 'rect', attr)

def main():
	arr = db_loader(PATH_TO_DB, 'август')
	wr = SVGbuilder(arr)
	wr.made_events()

# def main():
# 	self.root = ET.Element('svg', {'xmlns': r'http://www.w3.org/2000/svg', 'viewBox': '0 0 800 500'})
# 	events = []
# 	for i in COLMNS:
# 		events.append(ET.SubElement(self.root, 'rect', {'x': i,
# 												   'y': UPLINE,
# 												   'width': '70',
# 												   'height': temp_h,
# 												   'rx': '5',
# 												   'ry': '5',
# 												   'fill': '#505EE2'}))
# 	tree = ET.ElementTree(self.root)

# 	tree.write('image.svg')
# 	print('Готово')


if __name__ == '__main__':
	main()