package com.mrozekma.helmtaskerplugin;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.EditText;


public class EditMessage extends Activity {
	private static int DESCRIPTION_LENGTH = 60;
	private static int[] IDS = {R.id.host, R.id.exchange, R.id.username, R.id.password, R.id.message};
	private static String[] KEYS = {SendMessage.BUNDLE_EXTRA_HOST, SendMessage.BUNDLE_EXTRA_EXCHANGE, SendMessage.BUNDLE_EXTRA_USERNAME, SendMessage.BUNDLE_EXTRA_PASSWORD, SendMessage.BUNDLE_EXTRA_MESSAGE};
	static {
		assert(IDS.length == KEYS.length);
	}

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		final Intent intent = this.getIntent();
		if(intent != null) {
			for(int i = 0; i < IDS.length; i++) {
				final String value = intent.getStringExtra(KEYS[i]);
				if(value != null) {
					((EditText) this.findViewById(IDS[i])).setText(value);
				}
			}
		}
	}

	@Override
	public void finish() {
		final Bundle bundle = new Bundle();
		for(int i = 0; i < IDS.length; i++) {
			bundle.putString(KEYS[i], ((EditText)this.findViewById(IDS[i])).getText().toString());
		}

		final Intent intent = new Intent();
		intent.putExtra(com.twofortyfouram.locale.Intent.EXTRA_BUNDLE, bundle);
		final String message = ((EditText)this.findViewById(R.id.message)).getText().toString();
		intent.putExtra(com.twofortyfouram.locale.Intent.EXTRA_STRING_BLURB, (message.length() <= DESCRIPTION_LENGTH) ? message : message.substring(0, DESCRIPTION_LENGTH));

		this.setResult(RESULT_OK, intent);
		super.finish();
	}
}
