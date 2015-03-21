from json import loads as fromJS
import re

ws = re.compile('^([ \t]*)')
word = re.compile('^([a-zA-Z0-9_-]*)')
atom = re.compile('^([^ ]*)')
#TODO Will probably need to deal with escaped quotes someday
quotedAtom = re.compile('^"([^"]*)"')
atomNoParen = re.compile('^([^ )]*)')

class ParseError(RuntimeError):
	def __init__(self, msg):
		super(ParseError, self).__init__(msg)

class Parser:
	def __init__(self, data):
		self.data = data
		self.pos = 0

	def here(self):
		return self.data[self.pos:]

	def attempt(self, *strs):
		self.consumeWhitespace()
		for str in strs:
			if self.here().startswith(str):
				self.pos += len(str)
				return str
		return None

	def consume(self, str):
		self.consumeAny(str)

	def consumeAny(self, *strs):
		rtn = self.attempt(*strs)
		if rtn is None:
			self.fail()
		return rtn

	def consumeWord(self, restricted = True, noParen = False):
		self.consumeWhitespace()
		if self.here().startswith('"'):
			m = quotedAtom.match(self.here())
			self.pos += 2
		elif restricted:
			m = word.match(self.here())
		elif noParen:
			m = atomNoParen.match(self.here())
		else:
			m = atom.match(self.here())
		if m:
			self.pos += len(m.group(1))
			return m.group(1)
		self.fail()

	def consumeJSON(self):
		self.consumeWhitespace()
		rtn = self.consumeToEOL()
		if rtn.endswith(';'):
			rtn = rtn[:-1]
		return rtn

	def consumeWhitespace(self):
		m = ws.match(self.here())
		if m:
			self.pos += len(m.group(1))
		if self.here().startswith('//') or self.here().startswith('\n'):
			self.consumeToEOL()
			self.consumeWhitespace()

	def consumeEOL(self):
		if self.here() == '':
			return
		elif self.here()[0] == '\n':
			self.pos += 1
		else:
			self.fail()

	def consumeToEOL(self):
		nl = self.data.find('\n', self.pos)
		if nl == -1:
			rtn = self.data[self.pos:]
			self.pos = len(self.data)
		else:
			rtn = self.data[self.pos:nl]
			self.pos = nl + 1
		return rtn

	def isDone(self):
		self.consumeWhitespace()
		return self.pos == len(self.data)

	def fail(self):
		line, col = self.getLineCol()
		msg = "Unexpected data at %d:%d: " % (line, col)
		line = self.data[self.pos - col:].replace('\t', ' ')
		if '\n' in line:
			line = line[:line.find('\n')]
		raise ParseError('\n' + msg + line + '\n' + (' ' * (len(msg) + col)) + '^')

	def getLineCol(self):
		line, col = 1, 0
		for i in xrange(self.pos):
			if self.data[i] == '\n':
				line += 1
				col = 0
			else:
				col += 1
		return line, col

	# Key exists: (key)
	# Key does not exist: (!key)
	# Key is value: (key == value)
	# Key is not value: (key != value)
	# Key is any of: (key == value || value2 || value3)
	def consumeFilter(self, trigger):
		self.consume('(')
		eq = True
		if self.attempt('!'):
			eq = False
		key = self.consumeWord()
		if self.attempt(')'):
			# (key) -- key must exist in message
			# (!key) -- key must not exist in message
			trigger.addFilter(key, eq, None)
			return
		if not eq: # (!key) is the only valid use of prefix-not -- can't do (!key == value)
			self.fail()
		if self.consumeAny('==', '!=') == '!=':
			eq = False
		values = {self.consumeWord(),}
		while self.attempt('||'):
			values.add(self.consumeWord())
		self.consume(')')
		trigger.addFilter(key, eq, values)

	def consumeAction(self, trigger):
		command = self.consumeAny('exec ', 'script ')
		if command == 'exec ':
			self.consume('(')
			args = []

			# Inner functions are to make a closure on their parameters
			def makeLambdaLit(lit): args.append(lambda _: lit)
			def makeLambdaVar(var): args.append(lambda msg: msg[var])
			def makeLambdaVarDef(var, default): args.append(lambda msg: msg[var] if var in msg else default)

			while not self.attempt(')'):
				if self.attempt('$'): # Variable
					if self.attempt('{'):
						var = self.consumeWord(False)
						if self.attempt('??'): # Default value
							default = self.consumeWord()
							makeLambdaVarDef(var, default)
						else: # No default. Add implicit filter
							trigger.addFilter(var, True, None)
							makeLambdaVar(var)
						self.consume('}')
					else: # No default. Add implicit filter
						var = self.consumeWord(False, True)
						trigger.addFilter(var, True, None)
						makeLambdaVar(var)
				else: # Literal
					lit = self.consumeWord(False, True)
					makeLambdaLit(lit)
			env = None
			if self.attempt('in'):
				env = fromJS(self.consumeJSON())
			self.attempt(';') # Optionally allow a semicolon at the end to match C
			trigger.addExec(args, env)
		elif command == 'script ':
			self.consume('(')
			moduleName = self.consumeWord(noParen = True)
			self.consume(')')
			self.attempt(';')
			module = __import__("scripts.%s" % moduleName, globals(), locals(), 'trigger')
			trigger.addFunction(module.trigger)
