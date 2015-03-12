from subprocess import Popen

class ExecAction:
	def __init__(self, args):
		self.args = args

	def run(self, backend, message):
		args = [fn(message) for fn in self.args]
		Popen(args)

class Trigger:
	def __init__(self):
		self.filters = []
		self.actions = []

	# key is the index into the message hash
	# eq is true if the key must exist/match, false if it must not exist/not match
	# values is the list of valid/invalid (depending on eq) message values, or None if the key's existence is all that matters
	def addFilter(self, key, eq, values):
		self.filters.append((key, eq, values))

	def addExec(self, args):
		self.actions.append(ExecAction(args))

	def apply(self, backend, message):
		for key, eq, values in self.filters:
			if eq != (key in message):
				return
			if values is not None and eq != (message[key] in values):
				return
		map(lambda action: action.run(backend, message), self.actions)
