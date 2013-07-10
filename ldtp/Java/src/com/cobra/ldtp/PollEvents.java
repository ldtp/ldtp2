package com.cobra.ldtp;
/*
LDTP v2 java client.

@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009-13 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See 'COPYING' in the source distribution for more information.

Headers in this file shall remain intact.
 */

import java.lang.reflect.Method;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.Hashtable;
import java.util.Enumeration;

public class PollEvents extends Thread {
	// Based on http://stackoverflow.com/questions/443708/callback-functions-in-java
	Hashtable<String, Callback> callbacks = new Hashtable<String, Callback>();
	boolean pollServer = false;
	Ldtp ldtp = null;
	public PollEvents(Ldtp ldtp) {
		pollServer = true;
		this.ldtp = ldtp;
	}
	public void addCallbacks(String eventType, Object obj, final boolean isStatic, final String methodName, final Object... args) {
		Callback cb = new Callback(eventType, obj, isStatic, methodName, args);
		callbacks.put(methodName, cb);
	}
	public void removeCallbacks(final String methodName) {
		if (callbacks.containsKey(methodName))
			callbacks.remove(methodName);
	}
	void callbackMethod(final Object obj, final boolean isStatic, final String methodName, final Object... args)
	{
		ExecutorService EXE = Executors.newSingleThreadExecutor();
		try {
			EXE.execute (
					new Runnable()
					{
						public void run ()
						{
							Class<?> c;
							Method method;
							try
							{
								if (isStatic) c = (Class<?>)obj;
								else c = obj.getClass();

								Class<?>[] argTypes = null;
								if (args != null)
								{
									argTypes = new Class<?> [args.length];
									for (int i=0; i<args.length; i++)
									{
										argTypes[i] = args[i].getClass();
									}
								}
								method = c.getDeclaredMethod(methodName, argTypes);
								method.invoke(obj, args);
							}
							catch(Exception e)
							{
								if (ldtp.debug)
									e.printStackTrace();
							}
						}
					}
					);
		} finally {
			EXE.shutdown();
		}
	}
	public void run() {
		String event;
		while(pollServer) {
			try {
				event = ldtp.pollEvents();
				if (event.equals("")) {
					// Sleep 1 second
					Thread.sleep(1000);
					continue;
				}
				/*
				[0] - Event type
		        [1] - Window name (methodName)
				 */
				 Enumeration<String> keys = callbacks.keys();
				while (keys.hasMoreElements()) {
					Object key = keys.nextElement();
					Callback cb = (Callback)callbacks.get(key);
					if (event.equals(cb.eventType)) {
						// eventType-windowName matched
						callbackMethod(cb.obj, cb.isStatic, cb.methodName, cb.args);
						break;
					}
				}
			} catch(InterruptedException ex) {
				break;
			}
		}
	}
}
