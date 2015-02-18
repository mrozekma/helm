package com.mrozekma.helmtaskerplugin;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;

import com.google.gson.Gson;
import com.mrozekma.helm.Helm;
import com.mrozekma.helm.HelmException;

import java.util.HashMap;

public class SendMessage extends BroadcastReceiver {
	static final String BUNDLE_EXTRA_HOST = "com.mrozekma.android.helm.extra.host";
	static final String BUNDLE_EXTRA_EXCHANGE = "com.mrozekma.android.helm.extra.exchange";
	static final String BUNDLE_EXTRA_USERNAME = "com.mrozekma.android.helm.extra.username";
	static final String BUNDLE_EXTRA_PASSWORD = "com.mrozekma.android.helm.extra.password";
	static final String BUNDLE_EXTRA_MESSAGE = "com.mrozekma.android.helm.extra.message";

	private final Gson gson = new Gson();

	@Override
	public void onReceive(final Context context, Intent intent) {
		final String host = intent.getStringExtra(BUNDLE_EXTRA_HOST);
		final String exchange = intent.getStringExtra(BUNDLE_EXTRA_EXCHANGE);
		final String username = intent.getStringExtra(BUNDLE_EXTRA_USERNAME);
		final String password = intent.getStringExtra(BUNDLE_EXTRA_PASSWORD);
		final String message = intent.getStringExtra(BUNDLE_EXTRA_MESSAGE);

		new Thread(new Runnable() {
			@Override
			public void run() {
				try {
					final Helm helm = new Helm(host, exchange, username, password);
					helm.send(message);
				} catch(HelmException e) {
					Log.e("helm", "HelmException", e);
					final StringBuffer s = new StringBuffer();
					s.append(e.getMessage());
					if(e.getCause() != null) {
						s.append(": ");
						s.append(e.getCause().getMessage());
					}

					new Handler(Looper.getMainLooper()).post(new Runnable() {
						@Override
						public void run() {
							Toast.makeText(context, s.toString(), Toast.LENGTH_LONG).show();
						}
					});
				}
			}
		}).start();
	}
}
