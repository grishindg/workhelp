#Создаем графику календаря
import xml.etree.ElementTree as ET

WORKERS = ['Даниил', 'Влад', 'Андрей', 'Марина', 'Арсений', 'Ольга', 'Василий','Денис']
FIRSTCLMN = 238
COLMNS = tuple((str(i) for i in range(203, 803, 75)))
UPLINE = '27'
LEFTLINE = '30'
EV_NAME_X = '114'
temp_h = '150'
temp_ev_w = '167'
# SECND_LINE
NAMES_Y = '18.5'
FONT_S = '18pt'
print(COLMNS)

def main():
	root = ET.Element('svg', {'xmlns': r'http://www.w3.org/2000/svg', 'viewBox': '0 0 800 500'})
	events = []
	for i in COLMNS:
		events.append(ET.SubElement(root, 'rect', {'x': i,
												   'y': UPLINE,
												   'width': '70',
												   'height': temp_h,
												   'rx': '5',
												   'ry': '5',
												   'fill': '#505EE2'}))
	tree = ET.ElementTree(root)

	tree.write('image.svg')
	print('Готово')


if __name__ == '__main__':
	main()