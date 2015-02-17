package com.mrozekma.helm;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.rabbitmq.client.*;

import java.io.IOException;
import java.lang.reflect.Type;
import java.util.Map;

public class Helm {
	private String exchange;
	private final Connection conn;
	private final Channel chan;

	private static final Type MESSAGE_TYPE = new TypeToken<Map<String, String>>() {}.getType();
	private final Gson gson = new Gson();

	public Helm() {
		this(new Config());
	}

	// WHY, JAVA?! Separate constructor so we can have a config object to use with this()
	private Helm(Config config) {
		this(config.get("server", "helm.mrozekma.com"), config.get("exchange", "helm"), config.get("username"), config.get("password"));
	}

	public Helm(String host, String exchange, String username, String password) {
		this.exchange = exchange;

		final ConnectionFactory factory = new ConnectionFactory();
		factory.setHost(host);
		factory.setUsername(username);
		factory.setPassword(password);

		try {
			this.conn = factory.newConnection();
			this.chan = this.conn.createChannel();
			this.chan.exchangeDeclare(this.exchange, "fanout");
		} catch(IOException e) {
			throw new HelmException("Server error", e);
		}
	}

	@Override
	protected void finalize() throws Throwable {
		this.chan.close();
		this.conn.close();
	}

	public void send(Map<String, String> data) {
		try {
			final String message = this.gson.toJson(data, MESSAGE_TYPE);
			if(message == null) {
				throw new HelmException("Send failed: invalid message");
			}
			this.chan.basicPublish(this.exchange, "", null, message.getBytes());
		} catch(IOException e) {
			throw new HelmException("Send error", e);
		}
	}

	public void onReceive(final ReceiveHandler cb) {
		try {
			final String queue = this.chan.queueDeclare().getQueue();
			this.chan.queueBind(queue, this.exchange, "");
			this.chan.basicConsume(queue, false, new DefaultConsumer(this.chan) {
				@Override
				public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
					final Map<String, String> message = (Map<String, String>) Helm.this.gson.fromJson(new String(body), MESSAGE_TYPE);
					if(cb.onReceive(message)) {
						Helm.this.chan.basicAck(envelope.getDeliveryTag(), false);
					}
				}
			});
		} catch(IOException e) {
			throw new HelmException("Receive hook error", e);
		}
	}
}
