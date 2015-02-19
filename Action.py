from json import loads as fromJS
from string import Template
from subprocess import Popen

class Action:
	def __init__(self):
		self.cmd = None
		self.message = None
		self.module = None
		self.filters = {}

	# value == True means the key just needs to exist in the message
	def filter(self, key, value = True, comparator = None):
		self.filters[key] = value, comparator

	def apply(self, backend, message):
		if (self.cmd is not None) + (self.message is not None) + (self.module is not None) != 1:
			raise ValueError("Bad state")

		for key, (value, equality) in self.filters.iteritems():
			if not key in message:
				if equality == '|=': # Default value
					message[key] = value
				else:
					return False
			if value != True:
				if equality == ':=' and message[key] != value:
					return False
				if equality == '!=' and message[key] == value:
					return False
		tmplt = Template(self.cmd or self.message or self.module)
		try:
			subst = tmplt.substitute(**message)
		except (KeyError, ValueError):
			return False

		if self.cmd is not None:
			# Run command
			print "Running: %s" % subst
			Popen(subst, shell = True)
		elif self.module is not None:
			args = {}
			if ' ' in subst:
				subst, args = subst.split(' ', 1)
				args = fromJS(args)
			print "Importing module: %s" % subst
			# Import module
			module = __import__("scripts.%s" % subst, globals(), locals(), 'trigger')
			module.trigger(backend, **args)
		elif self.message is not None:
			# Send message
			print "Sending: %s" % subst
			backend.send(fromJS(subst))
		return True
