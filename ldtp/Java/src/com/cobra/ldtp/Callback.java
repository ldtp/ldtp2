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

public class Callback {
	public String eventType;
	public Object obj;
	public boolean isStatic;
	public String methodName;
	public Object args;
	public Callback(String eventType, Object obj, final boolean isStatic, final String methodName, final Object... args) {
		this.eventType = eventType;
		this.obj = obj;
		this.isStatic = isStatic;
		this.methodName = methodName;
		this.args = args;
	}
}
