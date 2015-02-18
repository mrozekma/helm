package com.mrozekma.helm;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static com.mrozekma.helm.Utils.*;

class Config {
	private static final class Directive {
		public final Pattern pattern;
		public String[] groups;
		public Directive(Pattern pattern, String[] groups) {
			this.pattern = pattern;
			this.groups = groups;
		}
	}

	private static final String FILENAME = "~/.helm";
	private static final Directive[] CONFIG_DIRECTIVES;

	static {
		final String[][] patterns = {
				{"Server ([^ ]+)", "server"},
				{"Server ([^ ]+) ([^ ]+)", "server", "exchange"},
				{"(?:Auth|Authentication|Credentials) ([^ ]+) (.+)", "username", "password"},
				{"LogFile (.+)", "logfile"},
				{"PidFile (.+)", "pidfile"},
		};
		CONFIG_DIRECTIVES = new Directive[patterns.length];
		for(int i = 0; i < CONFIG_DIRECTIVES.length; i++) {
			CONFIG_DIRECTIVES[i] = new Directive(Pattern.compile(patterns[i][0]), Arrays.copyOfRange(patterns[i], 1, patterns[i].length));
		}
	}

	private final Map<String, String> config = new HashMap<String, String>();

	public Config() {
		this(FILENAME);
	}

	public Config(String filename) {
		this(filename, false);
	}

	public Config(String filename, boolean strict) {
		filename = expanduser(filename);
		try {
			final Scanner s = new Scanner(new File(filename));
			while(s.hasNextLine()) {
				final String line = s.nextLine();
				boolean matched = false;
				for(Directive directive : CONFIG_DIRECTIVES) {
					final Matcher match = directive.pattern.matcher(line);
					if(match.matches()) {
						matched = true;
						try {
							assert match.groupCount() == directive.groups.length;
							for(int i = 0; i < directive.groups.length; i++) {
								this.config.put(directive.groups[i], match.group(i));
							}
						} catch(Exception e) {
							throw new HelmException("Unable to parse configuration directive", e);
						}
						break;
					}
				}
				if(!matched && strict) {
					throw new HelmException("Unrecognized configuration directive: " + line);
				}
			}
		} catch(IOException e) {
			throw new HelmException("Unable to read configuration file", e);
		}
	}

	public boolean has(String option) {
		return this.config.containsKey(option);
	}

	public String get(String option, String defaultValue) {
		return this.has(option) ? this.get(option) : defaultValue;
	}

	public String get(String option) {
		if(this.has(option)) {
			return this.config.get(option);
		} else {
			throw new HelmException("No configuration entry: " + option);
		}
	}
}
