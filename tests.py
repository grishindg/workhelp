# import re
# #3 1200 2400 // 3 2200 4 1200
# t = re.compile(r'[1-3]?\d (?:[0-1]?[0-9]|2[0-4])[0-5]\d (?:[1-3]?\d )?(?:[0-1]?[0-9]|2[0-4])[0-5]\d')
# #                число     время 800 или 0800    59макс    возможн другой день и тоже самое 

# mt = re.compile(r'([1-3]?\d) ((?:[0-1]?[0-9]|2[0-4])[0-5]\d) ((?:[1-3]?\d) )?((?:[0-1]?[0-9]|2[0-4])[0-5]\d)')
# mt2 = re.compile(r'((?:[0-1]?[0-9]|2[0-4]))')
# ls = ['24', '19', '00', '21', '25', '5', '05', '23']
# ls2 =('2 2400 2400',
# 	  '1 2359 2 1200',
# 	  '31 500 2300',
# 	  '32 1200 1 1200',
# 	  '45 600 0600')

# for i in ls2:
# 	# print(mt2.fullmatch(i))
# 	t = mt.fullmatch(i)
# 	if t:
# 		print(t.groups())
# 	else:
# 		print('не полное соответсвие')
def timetest():
	import datetime as dt
	d = dt.datetime(year=2020, month=9, day=12)
	t = d.timestamp()
	print(d.day, type(d.day))
if __name__ == '__main__':
	timetest()