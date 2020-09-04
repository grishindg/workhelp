#работает отдельно от fastman
import sqlite3
from openpyxl import load_workbook


PATH_TO_DB = './files/events.db'
EXFILE = './files/events.xlsx'
def create_table(db):
	conn = sqlite3.connect(db)
	curs = conn.cursor()
	curs.execute('CREATE TABLE events (name TEXT PRIMARY KEY,\
									   duration TEXT, masters TEXT)')
	conn.commit()
	conn.close()
	print('Создали таблицу')

def insert_todb(db, exfile):
	wb = load_workbook(exfile, read_only=True)
	sheet = wb['events']

	conn = sqlite3.connect(db)
	curs = conn.cursor()

	for i in range(1, 300):
		if sheet[i][1].value == 'stop':
			# print('Достигнут stop')
			break
		conn.execute("INSERT INTO events \
					  VALUES ('{}', '{}', '{}')".format(sheet[i][1].value, 
					   							 	  sheet[i][2].value, 
					   							 	  sheet[i][3].value))
	conn.commit()
	conn.close()
	wb.close()
	print('база данных заполнена')
if __name__ == '__main__':
	# create_table(PATH_TO_DB)
	insert_todb(PATH_TO_DB, EXFILE)