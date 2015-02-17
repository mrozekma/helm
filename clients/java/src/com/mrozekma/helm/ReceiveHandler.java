package com.mrozekma.helm;

import java.util.Map;

public interface ReceiveHandler {
	public boolean onReceive(Map<String, String> data);
}
