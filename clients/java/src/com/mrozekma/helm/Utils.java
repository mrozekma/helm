package com.mrozekma.helm;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Collections;
import java.util.Map;
import java.util.regex.Pattern;

public class Utils {
	// Ported from Python
	// I'm not willing to add an accessor for getpwnam(), so this assumes /home
	public static String expanduser(String path) {
		if(!path.startsWith("~")) {
			return path;
		}

		int i = path.indexOf('/', 1);
		if(i < 0) {
			i = path.length();
		}

		String userhome;
		if(i == 1) {
			userhome = System.getenv("HOME");
			if(userhome == null) {
				userhome = "/home/" + System.getProperty("user.name");
			}
		} else {
			userhome = "/home/" + path.substring(1, i);
		}

		if(userhome.endsWith("/")) {
			userhome = userhome.substring(0, userhome.length() - 1);
		}
		userhome += path.substring(i);
		return userhome.isEmpty() ? "/" : userhome;
	}

	// Oh Java. Why do you test me so
	// http://stackoverflow.com/a/15596145/309308
	@SuppressWarnings("unchecked")
	public static Map<String, Integer> getNamedGroups(Pattern regex)
			throws NoSuchMethodException, SecurityException,
			IllegalAccessException, IllegalArgumentException,
			InvocationTargetException {

		Method namedGroupsMethod = Pattern.class.getDeclaredMethod("namedGroups");
		namedGroupsMethod.setAccessible(true);

		Map<String, Integer> namedGroups = null;
		namedGroups = (Map<String, Integer>) namedGroupsMethod.invoke(regex);

		if(namedGroups == null) {
			throw new InternalError();
		}

		return Collections.unmodifiableMap(namedGroups);
	}
}
