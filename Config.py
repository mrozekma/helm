import argparse
from os.path import expanduser
from ConfigParser import ConfigParser, NoSectionError, NoOptionError

FILENAME = expanduser('~/.helm')

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--conf', help = 'Configuration file', dest = 'conf', default = FILENAME)
parser.add_argument('--test', action = 'store_true', dest = 'test', default = False)
args = parser.parse_args()

config = ConfigParser()
config.read([args.conf])

NO_DEFAULT = object()
def get(section, option, default = NO_DEFAULT):
	try:
		return config.get(section, option)
	except (NoSectionError, NoOptionError):
		if default is NO_DEFAULT:
			raise
		else:
			return default
