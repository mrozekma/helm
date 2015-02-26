from json import loads as fromJS, dumps as toJS
import pika

from threading import Thread

class ReceiveThread(Thread):
	def __init__(self, chan, queue, cb):
		Thread.__init__(self)
		self.chan = chan
		self.queue = queue
		self.cb = cb
		self.daemon = True

	def run(self):
		for method, properties, body in self.chan.consume(self.queue):
			result = self.cb(fromJS(body))
			if result != False:
				self.chan.basic_ack(method.delivery_tag)

class Backend:
	def __init__(self, host, exchange, username, password):
		self.exchange = exchange
		creds = pika.PlainCredentials(username, password)
		self.conn = pika.BlockingConnection(pika.ConnectionParameters(host = host, credentials = creds))
		self.chan = self.conn.channel()
		self.chan.exchange_declare(exchange = self.exchange, type = 'fanout')

	def __del__(self):
		try:
			self.chan.close()
			self.conn.close()
		except RuntimeError: # concurrent poll() invocation
			pass
		except TypeError:
			pass

	def send(self, data):
		self.chan.basic_publish(exchange = self.exchange, routing_key = '', body = toJS(data))

	def onReceive(self, cb):
		queue = self.chan.queue_declare().method.queue
		self.chan.queue_bind(exchange = self.exchange, queue = queue)
		ReceiveThread(self.chan, queue, cb).start()
