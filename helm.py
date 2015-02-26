#!/usr/bin/python
from json import loads as fromJS
import os
import re
import sys
import time

from Backend import Backend
from Config import initCLI as initConfig, get as getConfig, has as hasConfig, actions

if __name__ == '__main__':
	args = initConfig()

backend = Backend(
	getConfig('server', 'helm.mrozekma.com'),
	getConfig('exchange', 'helm'),
	getConfig('username'),
	getConfig('password')
)

if __name__ == '__main__':
	if args.send:
		pattern = re.compile('([a-zA-Z_][a-zA-Z0-9_]*): ?(.*)')
		try:
			message = {}
			for param in args.send:
				match = pattern.match(param)
				if not match:
					raise ValueError
				k, v = match.groups()
				message[k] = fromJS(v) # Can raise ValueError
		except ValueError, e:
			print "Unable to send: invalid message format"
			exit(1)
		backend.send(message)
		print "Message broadcast"
		exit(0)

	def onReceive(message):
		print "Received: %s" % message
		map(lambda action: action.apply(backend, message), actions)

	if args.daemon:
		if hasConfig('logfile'):
			logFile = getConfig('logfile')
		elif os.access('/var/log/helm', os.W_OK):
			logFile = '/var/log/helm/helm.log'
		elif os.access('/tmp', os.W_OK):
			logFile = '/tmp/helm.log'
		else:
			logFile = None

		if logFile is not None:
			print "Logging to %s" % logFile

		# Double-fork
		if os.fork() != 0:
			os._exit(0)
		os.setsid()
		if os.fork() != 0:
			os._exit(0)

		# Point the standard file descriptors at a log file
		if logFile is not None:
			log = file(logFile, 'a+', 0)
			devNull = file('/dev/null', 'r')
			os.dup2(devNull.fileno(), sys.stdin.fileno())
			os.dup2(log.fileno(), sys.stdout.fileno())
			os.dup2(log.fileno(), sys.stderr.fileno())

	pidFile = args.pidfile or getConfig('pidfile', None)
	if pidFile is not None:
		with open(pidFile, 'w') as f:
			f.write("%d\n" % os.getpid())

	backend.onReceive(onReceive)

	while True:
		time.sleep(1)
