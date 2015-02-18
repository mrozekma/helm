from string import Template
from subprocess import Popen

class Action:
	def __init__(self, cmd):
		self.cmd = cmd
		self.filters = {}

	# value == True means the key just needs to exist in the message
	def filter(self, key, value = True):
		self.filters[key] = value

	def apply(self, message):
		for key, value in self.filters.iteritems():
			if not key in message:
				return False
			if value != True and message[key] != value:
				return False

		tmplt = Template(self.cmd)
		try:
			cmd = tmplt.substitute(**message)
		except (KeyError, ValueError):
			return False

		Popen(cmd, shell = True)
		return True
