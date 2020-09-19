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


class SVGwriter():
	def __init__(self):
		self.root = ET.Element('svg', {'xmlns': r'http://www.w3.org/2000/svg', 'viewBox': '0 0 530 500'})
		self.specs = ('Школа Жен','Голубой Щенок', 'Ревизор', 'Кукла Для Невесты', 'Моя Прекрасная Леди', \
					  'Волки И Овцы', 'Матросская Тишина', 'Катерина Ильвовна', 'Ловушка для Наследника', \
					  'Чайка', 'И Никого Не Стало')
		self.workers = ('Даниил', 'Влад', 'Андрей', 'Марина', 'Арсений', 'Ольга', 'Василий', 'Денис')
		self.colmns = tuple((i for i in range(203, 523, 40)))
		self.leftline = '30'
		self.ev_name_x = '114'

		self.ev_w = '167'
		self.ev_h = '27'



		self.vb_width = '800'
		self.vb_height = 20


		self.stdBzAttrs = {'width': '39', 'height': self.ev_h, 'rx': '5', 'ry': '5', 'fill': '#36383F'}
		self.stdEvAttrs = {'x': self.leftline, 'width': self.ev_w, 'height': self.ev_h, 'rx': '5', 'ry': '5', 'stroke': '#36383F', 'fill': 'None'}
		self.stdTxAttrs = {'font-size': '9', 'text-anchor': 'middle', 'font-family': 'sans-serif', 'fill': '#36383F'}

	def saveSvg(self, ev_arr):

		locale.setlocale(locale.LC_TIME, "ru_RU")
		tm_fr = r'%H:%M'


		#отрисовка имен
		for name, x in zip(self.workers, self.colmns):
			attr = {'x': str(x+19), 'y': '18.5', 'fill': '#36383F'}
			attr.update(self.stdTxAttrs)
			n = ET.SubElement(self.root, 'text', attr)
			n.text = name



		d = 0

		y = 27
		old_y = 27

		for ev in ev_arr:

			start = dt.datetime.fromtimestamp(ev.start)
			finish = dt.datetime.fromtimestamp(ev.finish)

			#отрисовка квадрата события
			attr = self.stdEvAttrs.copy()
			attr.update({'y': str(y)})
			ET.SubElement(self.root, 'rect', attr)
			#Имя события
			attr = self.stdTxAttrs.copy()
			attr.update({'x': self.ev_name_x, 'y': str(y+16), 'font-size': '11'})
			sbnm = ET.SubElement(self.root, 'text', attr)
			if ev.name in self.specs:
				sbnm.set('font-weight', 'bold')
			sbnm.text = ev.name
			#время начала
			attr.update({'x': '194', 'y': str(y+8), 'font-size': '9', 'text-anchor': 'end'})
			sbst = ET.SubElement(self.root, 'text', attr)
			sbst.text = start.strftime(tm_fr)
			#время конца
			attr.update({'y': str(y+25)})
			sbfn = ET.SubElement(self.root, 'text', attr)
			sbfn.text = finish.strftime(tm_fr)

			if d < start.day:

				if not d % 2:
					self.drawGreyBox(str(old_y), str(y-old_y))
				old_y = y

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


			y += 29

		self.drawVertLines()
		self.root.attrib.update({'viewBox': f'0 0 530 {y+40}'})

		vlines = self.root.findall('./line[@class="vert"]')
		for vl in vlines:
			vl.attrib.update({'y2': str(y)})

		tree = ET.ElementTree(self.root)

		tree.write('./files/image.svg', encoding="utf-8")
		self.root = ET.Element('svg', {'xmlns': r'http://www.w3.org/2000/svg', 'viewBox': '0 0 530 500'})

		print('Изображение сохранено ')

	def drawGreyBox(self, y, height):
		attr = {'x': '203', 'y': y, 'width': '319', 'height': height, 'fill': '#F0F0F0'}
		self.root.insert(0, ET.Element('rect', attr))

	def drawline(self, y, day=False):
		attr = {'x1': '200', 'x2': '522', 'y1': str(y-1), 'y2': str(y-1), 'stroke': '#AAAAAA', 'fill': 'None', 'stroke-width': '0.5'}
		if day:
			attr.update({'stroke-width': '1', 'stroke': '#36383F', 'x1': '5'})
		ET.SubElement(self.root, 'line', attr)

	def drawVertLines(self):
		for i in self.colmns:
			attr = {'x1': str(i-0.5), 'x2': str(i-0.5), 'y1': '28',
					'y2': '60', 'stroke': '#AAAAAA', 'fill': 'None',
					'stroke-width': '0.5', 'class': 'vert'}
			ET.SubElement(self.root, 'line', attr)

	def drawBzBox(self, index, y):
		'''рисует бокс занятости'''
		attr = {'y': str(y), 'x': str(self.colmns[index])}
		attr.update(self.stdBzAttrs)
		ET.SubElement(self.root, 'rect', attr)



def main():
	arr = db_loader(PATH_TO_DB, 'сентябрь')
	wr = SVGwriter()
	wr.saveSvg(arr)

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
# 												   'fill': '#36383F'}))
# 	tree = ET.ElementTree(self.root)

# 	tree.write('image.svg')
# 	print('Готово')


if __name__ == '__main__':
	main()