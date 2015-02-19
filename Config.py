import argparse
from os.path import expanduser
import re
from string import Template

from Action import Action

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
actions = []

def initModule(filename = FILENAME):
	"""Called when helm is imported by another python script"""
	try:
		with open(filename) as f:
			for line in f:
				# Special-case actions
				if line.startswith('Action '):
					line = line[len('Action '):]
					act = Action()
					while line != '':
						match = ACTION_FILTER.match(line)
						if match:
							key, comparator, value, line = match.groups()
							act.filter(key, True if value is None else value, comparator)
						else:
							break
					if line.startswith('->'): # Trigger a message
						line = line[2:].lstrip(' ')
						act.message = line
					elif line.startswith('<-'): # Import a script
						line = line[2:].lstrip(' ')
						act.module = line
					else: # Execute a command
						act.cmd = line
					actions.append(act)
					continue
				for pattern in CONFIG_DIRECTIVES:
					match = pattern.match(line)
					if match:
						config.update(match.groupdict())
						break
				else:
					print "Unrecognized configuration directive: %s" % line
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
