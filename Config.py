import argparse
from os.path import expanduser
import re
from string import Template

from Action import Action
from ParseConfig import Parser
from Trigger import Trigger

FILENAME = expanduser('~/.helm')
CONFIG_DIRECTIVES = map(re.compile, [
	'^$', # Skip blank lines
	'#.*', # Skip comments
	'Server (?P<server>[^ ]+)',
	'Server (?P<server>[^ ]+) (?P<exchange>[^ ]+)',
	'(?:Auth|Authentication|Credentials) (?P<username>[^ ]+) (?P<password>.+)',
	'LogFile (?P<logfile>.+)',
	'PidFile (?P<pidfile>.+)',
])
ACTION_FILTER = re.compile('\(([^ :()]+)(?: ?(:=|!=|\|=) ?([^)]+))?\) *(.*)$')

# Default values
config = {
	'server': 'helm.mrozekma.com',
	'exchange': 'helm',
	# 'username': None,
	# 'password': None,
	# 'logfile': None,
	# 'pidfile': None,
}
triggers = []

def initModule(filename = FILENAME):
	"""Called when helm is imported by another python script"""
	try:
		with open(filename) as f:
			parser = Parser(f.read())
			while not parser.isDone():
				directive = parser.consumeAny('server ', 'auth ', 'authentication ', 'credentials ', 'logfile ', 'pidfile ', 'trigger ')
				if directive == 'server ':
					config['server'] = parser.consumeWord()
					parser.consumeEOL()
				elif directive in ('auth ', 'authentication ', 'credentials '):
					config['username'] = parser.consumeWord()
					config['password'] = parser.consumeWord()
					parser.consumeEOL()
				elif directive == 'logfile ':
					config['logfile'] = parser.consumeWord()
					parser.consumeEOL()
				elif directive == 'pidfile ':
					config['pidfile'] == parser.consumeWord()
					parser.consumeEOL()
				elif directive == 'trigger ':
					trigger = Trigger()
					triggers.append(trigger)
					while not parser.attempt('{'):
						parser.consumeFilter(trigger)
					while not parser.attempt('}'):
						parser.consumeAction(trigger)
		return True
	except IOError:
		return False

def initCLI():
	"""Called when running helm.py from the command-line"""
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--conf', help = 'Configuration file', dest = 'conf', default = FILENAME)
	parser.add_argument('-n', '--no-detach', help = 'Stay in foreground', action = 'store_false', dest = 'daemon', default = True)
	parser.add_argument('--pidfile', help = 'Write PID to this file', dest = 'pidfile', default = None)
	parser.add_argument('--send', help = 'Send a helm message', nargs = '+', dest = 'send', default = None)
	args = parser.parse_args()
	initModule(args.conf)
	return args

def has(option):
	return option in config

NO_DEFAULT = object()
def get(option, default = NO_DEFAULT):
	if has(option):
		return config[option]
	elif default is not NO_DEFAULT:
		return default
	else:
		raise ValueError("No configuration entry: %s" % option)
