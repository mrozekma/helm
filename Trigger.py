from subprocess import Popen
import traceback

class ExecAction:
	def __init__(self, args, env):
		self.args = args
		self.env = env

	def run(self, backend, message):
		args = [fn(message) for fn in self.args]
		Popen(args, env = self.env).wait()

class FunctionAction:
	def __init__(self, fn):
		self.fn = fn

	def run(self, backend, message):
		print message
		self.fn(backend, **message)

class SendAction:
	def __init__(self, message):
		self.message = message

	def run(self, backend, message):
		backend.send(self.message)

class Trigger:
	def __init__(self):
		self.filters = []
		self.actions = []

	# key is the index into the message hash
	# eq is true if the key must exist/match, false if it must not exist/not match
	# values is the list of valid/invalid (depending on eq) message values, or None if the key's existence is all that matters
	def addFilter(self, key, eq, values):
		self.filters.append((key, eq, values))

	def addExec(self, args, env = None):
		self.actions.append(ExecAction(args, env))

	def addFunction(self, fn):
		self.actions.append(FunctionAction(fn))

	def addSend(self, message):
		self.actions.append(SendAction(message))

	def apply(self, backend, message):
		for key, eq, values in self.filters:
			if eq != (key in message):
				return
			if values is not None and eq != (message[key] in values):
				return
		for action in self.actions:
			try:
				action.run(backend, message)
			except Exception:
				traceback.print_exc()
