/*
LDTP v2 java callback test client.

@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009-12 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See 'COPYING' in the source distribution for more information.

Headers in this file shall remain intact.
*/
import com.cobra.ldtp;

public class CallbackTest {
    public void callbackMethodNoArgs(Object... dummyArgs) {
	/* With no args, getting the following exception
	 * 	java.lang.NoSuchMethodException: com.cobra.ldtp.CallbackTest.callbackMethodNoArgs([Ljava.lang.Object;)
	 *	at java.lang.Class.getDeclaredMethod(Unknown Source)
	 *  at com.cobra.ldtp.PollEvents$1.run(PollEvents.java:72)
	 *  at java.util.concurrent.ThreadPoolExecutor.runWorker(Unknown Source)
	 *  at java.util.concurrent.ThreadPoolExecutor$Worker.run(Unknown Source)
	 * 	at java.lang.Thread.run(Unknown Source)
	 * and so using dummyArgs
	 */
	System.out.println("callbackMethodNoArgs");
    }
    public void callbackMethodWithArgs(Object... args) {
	System.out.println("callbackMethodWithArgs");
	for (int i=0; i<args.length; i++) {
	    System.out.println(args[i]);
	}
    }
    public static void main(String[] args) {
    	Ldtp ldtp = new Ldtp("Open");
    	CallbackTest cbTest = new CallbackTest();
    	System.out.println(ldtp.onWindowCreate(cbTest, false, "callbackMethodNoArgs"));
    	ldtp.setWindowName("*Notepad");
    	ldtp.selectMenuItem("File;Open");
    	ldtp.setWindowName("Open");
    	ldtp.waitTillGuiExist();
    	ldtp.click("Cancel");
    	ldtp.waitTillGuiNotExist();
    	ldtp.removeCallback();
    	ldtp.waitTime(1);
    	System.out.println(ldtp.onWindowCreate(cbTest, false, "callbackMethodWithArgs", "Hello", "World", 1, 2, 3));
    	ldtp.setWindowName("*Notepad");
    	ldtp.selectMenuItem("File;Open");
    	ldtp.setWindowName("Open");
    	ldtp.waitTillGuiExist();
    	ldtp.click("Cancel");
    	ldtp.waitTillGuiNotExist();
    	ldtp.removeCallback();
    }
}
