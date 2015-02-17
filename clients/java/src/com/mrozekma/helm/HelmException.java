package com.mrozekma.helm;

public class HelmException extends RuntimeException {
	public HelmException(String message) {
		super(message);
	}

	public HelmException(String message, Throwable cause) {
		super(message, cause);
	}
}
