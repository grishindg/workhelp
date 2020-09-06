import re

dateRe = re.compile(r'([1-3]?\d) ((?:[0-1]?[0-9]|2[0-4])[0-5]\d) ((?:[1-3]?\d) )?((?:[0-1]?[0-9]|2[0-4])[0-5]\d)')

class TotEvents():
	def __init__(self, name, start, finish, members, notes = ''):
		self.name = name
		self.start = start
		self.finish = finish
		self.members = members
		self.notes = notes
