/*
LDTP v2 java test client.

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

public class LdtpTest {
    public static void main(String[] args) {
	/*
	int i;
	Ldtp ldtp = new Ldtp("*-gedit");
	String[] windowList = ldtp.getWindowList();
	for(i = 0; i < windowList.length; i++)
	    System.out.print(windowList[i]);
	System.out.println("");
	String[] appList = ldtp.getAppList();
	for(i = 0; i < appList.length; i++)
	    System.out.print(appList[i]);
	System.out.println("");
	String[] objList = ldtp.getObjectList();
	for(i = 0; i < objList.length; i++)
	    System.out.print(objList[i] + " ");
	System.out.println("");
	try {
	    ldtp.setWindowName("Testing LDTP with Java Client");
	    objList = ldtp.getObjectList();
	    for(i = 0; i < objList.length; i++)
		System.out.print(objList[i] + " ");
	    System.out.println("");
	} catch (LdtpExecutionError ex) {
	    System.out.println(ex.getMessage());
	} finally {
	    ldtp.setWindowName("*-gedit");
	}
	Integer[] size = ldtp.getWindowSize();
	for(i = 0; i < size.length; i++)
	    System.out.print(size[i] + " ");
	System.out.println("");
	size = ldtp.getObjectSize("btnOpen");
	for(i = 0; i < size.length; i++)
	    System.out.print(size[i] + " ");
	System.out.println("");
	System.out.println(ldtp.guiExist());
	System.out.println(ldtp.guiExist("btnOpen"));
	System.out.println(ldtp.objectExist("btnOpen"));
	System.out.println(ldtp.selectMenuItem("mnuFile;mnuNew"));
	try {
	    System.out.println(ldtp.selectMenuItem("mnuFile;mnuDing"));
	} catch (LdtpExecutionError ex) {
	    System.out.println(ex.getMessage());
	}
	System.out.println(ldtp.doesMenuItemExist("mnuFile;mnuNew"));
	System.out.println(ldtp.doesMenuItemExist("mnuFile;mnuDing"));
	String[] subMenus = ldtp.listSubMenus("mnuFile");
	for(i = 0; i < subMenus.length; i++)
	    System.out.print(subMenus[i] + " ");
	System.out.println("");
	System.out.println(ldtp.imageCapture());
	System.out.println(ldtp.launchApp("gnome-terminal"));
	System.out.println(ldtp.waitTillGuiExist());
	ldtp.setWindowName("Testing LDTP with Java Client");
	System.out.println(ldtp.waitTillGuiExist(5));
	ldtp.setWindowName("*-gedit");
	System.out.println(ldtp.getTextValue("txt1"));
	System.out.println(ldtp.click("btnNew"));
	*/
	Ldtp ldtp = new Ldtp("*Notepad");
	System.out.println(ldtp.getTextValue("txt0"));
    }
}
