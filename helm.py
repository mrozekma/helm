#!/usr/bin/python
import os

from Backend import Backend
from Config import initCLI as initConfig, get as getConfig, has as hasConfig

if __name__ == '__main__':
	args = initConfig()

backend = Backend(
	getConfig('server', 'server', 'helm.mrozekma.com'),
	getConfig('server', 'exchange', 'helm'),
	getConfig('host', 'username'),
	getConfig('host', 'password')
)

if __name__ == '__main__':
	if args.test:
		backend.send({'foo': 'bar'})
		exit(0)
	else:
		def cb(data):
			print "receive: %s" % data
		backend.onReceive(cb)

	if args.daemon:
		if hasConfig('host', 'log'):
			logFile = getConfig('host', 'log')
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
			log = os.open(logFile, os.O_CREAT | os.O_RDWR)
			os.dup2(log, 0)
			os.dup2(log, 1)
			os.dup2(log, 2)

	pidfile = args.pidfile or getConfig('host', 'pidfile', None)
	if pidfile is not None:
		with open(pidFile, 'w') as f:
			f.write("%d\n" % os.getpid())

	while True: pass
