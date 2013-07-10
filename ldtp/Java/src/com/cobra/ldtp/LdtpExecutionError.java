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

/**
 * LdtpExecutionError is a custom exception thrown incase of any failures in the communication between the server and Java client
 */
public class LdtpExecutionError extends RuntimeException {
	public LdtpExecutionError(String msg) {
		super(msg);
	}
}
