#!/usr/bin/python
from Backend import Backend
from Config import get as getConfig

backend = Backend(
	getConfig('server', 'server', 'helm.mrozekma.com'),
	getConfig('server', 'exchange', 'helm'),
	getConfig('host', 'username'),
	getConfig('host', 'password')
)

from Config import args
if args.test:
	backend.send({'foo': 'bar'})
else:
	def cb(data):
		print "receive: %s" % data
	backend.onReceive(cb)

while True: pass
