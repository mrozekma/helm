import argparse
from os.path import expanduser
from ConfigParser import ConfigParser, NoSectionError, NoOptionError

FILENAME = expanduser('~/.helm')

config = ConfigParser()
def initModule(filename = FILENAME):
	"""Called when helm is imported by another python script"""
	config.read([filename])

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

NO_DEFAULT = object()
def get(section, option, default = NO_DEFAULT):
	if config is None:
		parseConfig()
	try:
		return config.get(section, option)
	except (NoSectionError, NoOptionError):
		if default is NO_DEFAULT:
			raise
		else:
			return default

def has(section, option):
	if config is None:
		parseConfig()
	return config.has_option(section, option)
