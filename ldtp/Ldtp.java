/*
LDTP v2 ruby client.

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
// This file depends on apache jar files:
// http://mirror.cc.columbia.edu/pub/software/apache//commons/codec/binaries/commons-codec-1.6-bin.zip
// http://www.apache.org/dyn/closer.cgi/ws/xmlrpc/
// Ran the test in Ubuntu 11.04 as
// export CLASSPATH=apache-xmlrpc-3.1.3/lib/xmlrpc-client-3.1.3.jar:apache-xmlrpc-3.1.3/lib/xmlrpc-common-3.1.3.jar:.:apache-xmlrpc-3.1.3/lib/ws-commons-util-1.0.2.jar:commons-codec-1.6/commons-codec-1.6.jar
// java Ldtp
// Ran the test in Windows 7 SP1 like: (Adjusted the code accordingly for Windows, as I need to maniuplate with Notepad)
// java -cp xmlrpc-client-3.1.3.jar;xmlrpc-common-3.1.3.jar;ws-commons-util-1.0.2.jar;commons-codec-1.6.jar;. Ldtp
import java.net.URL;
import java.util.Arrays;
import java.io.FileOutputStream;
import java.lang.ProcessBuilder;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.commons.codec.binary.Base64;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;

class LdtpExecutionError extends RuntimeException {
    public LdtpExecutionError(String msg) {
	super(msg);
    }
}

class Ldtp {
    Process p = null;
    String windowName;
    String serverAddr;
    String serverPort;
    ProcessBuilder pb;
    Boolean windowsEnv = false;
    XmlRpcClient client = null;
    XmlRpcClientConfigImpl config = null;
    private void connectToServer() {
	serverAddr = System.getenv("LDTP_SERVER_ADDR");
	if (serverAddr == null)
	    serverAddr = "localhost";
	serverPort = System.getenv("LDTP_SERVER_PORT");
	if (serverPort == null)
	    serverPort = "4118";
	String tmpEnv = System.getenv("LDTP_WINDOWS");
	if (tmpEnv != null)
	    windowsEnv = true;
	else {
	    tmpEnv = System.getenv("LDTP_LINUX");
	    if (tmpEnv != null)
		windowsEnv = false;
	    else {
		String os = System.getProperty("os.name").toLowerCase();
		if (os.indexOf("win") >= 0)
		    windowsEnv = true;
	    }
	}
	config = new XmlRpcClientConfigImpl();
	//String url = String.fromat("http://%s:%s/RPC2", serverAddr, serverPort);
	String url = "http://localhost:4118/RPC2";
	try {
	    config.setServerURL(new URL(url));
	} catch (java.net.MalformedURLException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	}
	client = new XmlRpcClient();
	client.setConfig(config);
	Boolean isAlive = false;
	Object[] params = null;
	try {
	    isAlive = (Boolean)client.execute("isalive", params);
	} catch (org.apache.xmlrpc.XmlRpcException ex) {
	    ;
	} catch (Exception ex) {
	    ;
	}
	if (!isAlive) {
	    launchLdtpProcess();
	}
    }
    private void launchLdtpProcess() {
	if (windowsEnv)
	    pb = new ProcessBuilder("CobraWinLDTP.exe");
	else
	    pb = new ProcessBuilder("ldtp");
	try {
	    p = pb.start();
	    Runtime.getRuntime().addShutdownHook(new Thread() {
		    public void run() {
			terminateLdtpProcess();
		    }
		});
	} catch (java.io.IOException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	}
	try {
	    // Sleep 5 seconds
	    Thread.sleep(5000);
	} catch (java.lang.InterruptedException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	}
    }
    private void terminateLdtpProcess() {
	if (p != null) {
	    p.destroy();
	}
    }
    public Ldtp() {
	this(null);
    }
    public Ldtp(String windowName) {
	this.windowName = windowName;
	connectToServer();
    }
    public void setWindowName(String windowName) {
	this.windowName = windowName;
    }
    public String getWindowName() {
	return windowName;
    }
    private Object[] getJavaObjectList(String cmd, Object[] params) {
	try {
	    return (Object[])client.execute(cmd, params);
	} catch (org.apache.xmlrpc.XmlRpcException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	}
    }
    private Integer verifyAction(String cmd, Object[] params) {
	try {
	    return (Integer)client.execute(cmd, params);
	} catch (org.apache.xmlrpc.XmlRpcException ex) {
	    return 0;
	} catch (Exception ex) {
	    return 0;
	}
    }
    private Integer doAction(String cmd, Object[] params) {
	try {
	    return (Integer)client.execute(cmd, params);
	} catch (org.apache.xmlrpc.XmlRpcException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	}
    }
    private String getString(String cmd, Object[] params) {
	try {
	    return (String)client.execute(cmd, params);
	} catch (org.apache.xmlrpc.XmlRpcException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	}
    }
    private Integer getInt(String cmd, Object[] params) {
	try {
	    return (Integer)client.execute(cmd, params);
	} catch (org.apache.xmlrpc.XmlRpcException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	}
    }
    private Double getDouble(String cmd, Object[] params) {
	try {
	    return (Double)client.execute(cmd, params);
	} catch (org.apache.xmlrpc.XmlRpcException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	}
    }
    private Double[] getDoubleList(String cmd, Object[] params) {
	Double[] result = null;
	Object[] o = getJavaObjectList(cmd, params);
	result = Arrays.copyOf(o, o.length, Double[].class);
	return result;
    }
    private String[] getStringList(String cmd, Object[] params) {
	String[] result = null;
	Object[] o = getJavaObjectList(cmd, params);
	result = Arrays.copyOf(o, o.length, String[].class);
	return result;
    }
    private Integer[] getIntList(String cmd, Object[] params) {
	Integer[] result = null;
	Object[] o = getJavaObjectList(cmd, params);
	result = Arrays.copyOf(o, o.length, Integer[].class);
	return result;
    }
    // General
    public String[] getWindowList() throws LdtpExecutionError {
	return getStringList("getwindowlist", null);
    }
    public String[] getAppList() throws LdtpExecutionError {
	return getStringList("getapplist", null);
    }
    public String[] getObjectList() throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName};
	return getStringList("getobjectlist", params);
    }
    public String[] getObjectInfo(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getStringList("getobjectinfo", params);
    }
    public String[] getObjectInfo(String objName, String property) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, property};
	return getStringList("getobjectproperty", params);
    }
    public String[] getChild(String childName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, childName};
	return getStringList("getchild", params);
    }
    public String[] getChild(String childName, String role) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, childName, role};
	return getStringList("getchild", params);
    }
    public String[] getChild(String childName, String role, String property) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, childName, role, property};
	return getStringList("getchild", params);
    }
    public Integer[] getObjectSize(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getIntList("getobjectsize", params);
    }
    public Integer[] getWindowSize() throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName};
	return getIntList("getwindowsize", params);
    }
    public int reMap() {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName};
	return verifyAction("remap", params);
    }
    public int waitTime() {
	return waitTime(5);
    }
    public int waitTime(int timeout) {
	Object[] params = new Object[]{timeout};
	return doAction("wait", params);
    }
    public String getObjectNameAtCoords() {
	return getObjectNameAtCoords(0.0);
    }
    public String getObjectNameAtCoords(double waitTime) {
	Object[] params = new Object[]{waitTime};
	return getString("getobjectnameatcoords", params);
    }
    public int guiExist() {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName};
	return verifyAction("guiexist", params);
    }
    public int guiExist(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("guiexist", params);
    }
    public int waitTillGuiExist() {
	return waitTillGuiExist("", 30, "");
    }
    public int waitTillGuiExist(String objName) {
	return waitTillGuiExist(objName, 30, "");
    }
    public int waitTillGuiExist(String objName, int guiTimeOut) {
	return waitTillGuiExist(objName, guiTimeOut, "");
    }
    public int waitTillGuiExist(int guiTimeOut) {
	return waitTillGuiExist("", guiTimeOut, "");
    }
    public int waitTillGuiExist(int guiTimeOut, String state) {
	return waitTillGuiExist("", guiTimeOut, state);
    }
    public int waitTillGuiExist(String objName, int guiTimeOut, String state) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, guiTimeOut, state};
	return verifyAction("waittillguiexist", params);
    }
    public int waitTillGuiNotExist() {
	return waitTillGuiNotExist("", 30, "");
    }
    public int waitTillGuiNotExist(String objName) {
	return waitTillGuiNotExist(objName, 30, "");
    }
    public int waitTillGuiNotExist(String objName, int guiTimeOut) {
	return waitTillGuiNotExist(objName, guiTimeOut, "");
    }
    public int waitTillGuiNotExist(int guiTimeOut) {
	return waitTillGuiNotExist("", guiTimeOut, "");
    }
    public int waitTillGuiNotExist(int guiTimeOut, String state) {
	return waitTillGuiNotExist("", guiTimeOut, state);
    }
    public int waitTillGuiNotExist(String objName, int guiTimeOut, String state) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, guiTimeOut, state};
	return verifyAction("waittillguinotexist", params);
    }
    public int objectExist(String objName) {
	return guiExist(objName);
    }
    public int delayCmdExec(int delay) {
	Object[] params = new Object[]{delay};
	return verifyAction("delaycmdexec", params);
    }
    public int launchApp(String cmd) {
	Object[] params = new Object[]{cmd};
	return doAction("launchapp", params);
    }
    public int launchApp(String cmd, String[] args) {
	Object[] params = new Object[]{cmd, args};
	return doAction("launchapp", params);
    }
    public int launchApp(String cmd, String[] args, int delay) {
	Object[] params = new Object[]{cmd, args, delay};
	return doAction("launchapp", params);
    }
    public int launchApp(String cmd, String[] args, int delay, int env) {
	Object[] params = new Object[]{cmd, args, delay, env};
	return doAction("launchapp", params);
    }
    public int launchApp(String cmd, String[] args, int delay, int env, String lang) {
	Object[] params = new Object[]{cmd, args, delay, env, lang};
	return doAction("launchapp", params);
    }
    private String pollEvents() {
	return getString("poll_events", null);
    }
    public String getLastLog() {
	return getString("getlastlog", null);
    }
    public int startProcessMonitor(String processName) throws LdtpExecutionError {
	Object[] params = new Object[]{processName};
	return doAction("startprocessmonitor", params);
    }
    public int stopProcessMonitor(String processName, int interval) throws LdtpExecutionError {
	Object[] params = new Object[]{processName, interval};
	return doAction("stopprocessmonitor", params);
    }
    public Double[] getCpuStat(String processName) throws LdtpExecutionError {
	Object[] params = new Object[]{processName};
	return getDoubleList("getcpustat", params);
    }
    public Integer[] getMemoryStat(String processName) throws LdtpExecutionError {
	Object[] params = new Object[]{processName};
	return getIntList("getmemorystat", params);
    }
    public int windowUpTime() throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName};
	return doAction("windowuptime", params);
    }
    public int onWindowCreate() throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName};
	return doAction("onwindowcreate", params);
    }
    public int removeCallback() throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName};
	return doAction("removecallback", params);
    }
    public int registerEvent(String eventName) throws LdtpExecutionError {
	Object[] params = new Object[]{eventName};
	return doAction("registerevent", params);
    }
    public int deRegisterEvent(String eventName) throws LdtpExecutionError {
	Object[] params = new Object[]{eventName};
	return doAction("deRegisterevent", params);
    }
    public int registerKbEvent(String keys) throws LdtpExecutionError {
	Object[] params = new Object[]{keys};
	return doAction("registerevent", params);
    }
    public int registerKbEvent(String keys, int modifiers) throws LdtpExecutionError {
	Object[] params = new Object[]{keys, modifiers};
	return doAction("registerevent", params);
    }
    public int deRegisterKbEvent(String keys) throws LdtpExecutionError {
	Object[] params = new Object[]{keys};
	return doAction("deregisterevent", params);
    }
    public int deRegisterKbEvent(String keys, int modifiers) throws LdtpExecutionError {
	Object[] params = new Object[]{keys, modifiers};
	return doAction("deregisterevent", params);
    }
    public int maximizeWindow() throws LdtpExecutionError {
	return doAction("maximizewindow", null);
    }
    public int maximizeWindow(String windowName) throws LdtpExecutionError {
	Object[] params = new Object[]{windowName};
	return doAction("maximizewindow", params);
    }
    public int minimizeWindow() throws LdtpExecutionError {
	return doAction("minimizewindow", null);
    }
    public int minimizeWindow(String windowName) throws LdtpExecutionError {
	Object[] params = new Object[]{windowName};
	return doAction("minimizewindow", params);
    }
    public int closeWindow() throws LdtpExecutionError {
	return doAction("closewindow", null);
    }
    public int closeWindow(String windowName) throws LdtpExecutionError {
	Object[] params = new Object[]{windowName};
	return doAction("closewindow", params);
    }
    public int unMaximizeWindow() throws LdtpExecutionError {
	return doAction("unmaximizewindow", null);
    }
    public int unMaximizeWindow(String windowName) throws LdtpExecutionError {
	Object[] params = new Object[]{windowName};
	return doAction("unmaximizewindow", params);
    }
    public int unMinimizeWindow() throws LdtpExecutionError {
	return doAction("unminimizewindow", null);
    }
    public int unMinimizeWindow(String windowName) throws LdtpExecutionError {
	Object[] params = new Object[]{windowName};
	return doAction("unminimizewindow", params);
    }
    public int activateWindow(String windowName) throws LdtpExecutionError {
	Object[] params = new Object[]{windowName};
	return doAction("activatewindow", params);
    }
    public String[] getAllStates(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getStringList("getallstates", params);
    }
    public int hasState(String objName, String state) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, state};
	return verifyAction("hasstate", params);
    }
    public int hasState(String objName, String state, int guiTimeOut) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, state, guiTimeOut};
	return verifyAction("hasstate", params);
    }
    public int grabFocus(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("grabfocus", params);
    }
    public int click(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("click", params);
    }
    public int press(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("press", params);
    }
    public int check(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("check", params);
    }
    public int uncheck(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("uncheck", params);
    }
    public int verifyToggled(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifytoggled", params);
    }
    public int verifyCheck(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifycheck", params);
    }
    public int verifyUnCheck(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifyuncheck", params);
    }
    public int stateEnabled(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("stateenabled", params);
    }
    public int verifyPushButton(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifyPushButton", params);
    }
    public int getPanelChildCount(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getInt("getpanelchildcount", params);
    }
    public int selectPanel(String objName, int index) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, index};
	return doAction("selectpanel", params);
    }
    public int selectPanelName(String objName, String name) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, name};
	return doAction("selectpanelname", params);
    }
    // Menu
    public int selectMenuItem(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("selectmenuitem", params);
    }
    public int doesMenuItemExist(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("doesmenuitemexist", params);
    }
    public String[] listSubMenus(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getStringList("listsubmenus", params);
    }
    public int menuCheck(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("menucheck", params);
    }
    public int menuUnCheck(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("menuuncheck", params);
    }
    public int menuItemEnabled(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("menuitemenabled", params);
    }
    public int verifyMenuCheck(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifymenucheck", params);
    }
    public int verifyMenuUnCheck(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifymenuuncheck", params);
    }
    public int invokeMenu(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("invokemenu", params);
    }
    // Text
    public int generateKeyEvent(String data) throws LdtpExecutionError {
	Object[] params = new Object[]{data};
	return doAction("generatekeyevent", params);
    }
    public int keyPress(String data) throws LdtpExecutionError {
	Object[] params = new Object[]{data};
	return doAction("keypress", params);
    }
    public int keyRelease(String data) throws LdtpExecutionError {
	Object[] params = new Object[]{data};
	return doAction("keyrelease", params);
    }
    public int enterString(String data) throws LdtpExecutionError {
	Object[] params = new Object[]{data};
	return doAction("enterstring", params);
    }
    public int enterString(String objName, String data) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, data};
	return doAction("enterstring", params);
    }
    public int setTextValue(String objName, String data) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, data};
	return doAction("settextvalue", params);
    }
    public String getTextValue(String objName) throws LdtpExecutionError {
	return getTextValue(objName, 0, 0);
    }
    public String getTextValue(String objName, int startPos) throws LdtpExecutionError {
	return getTextValue(objName, startPos, 0);
    }
    public String getTextValue(String objName, int startPos, int endPos) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, startPos, endPos};
	return getString("gettextvalue", params);
    }
    public int verifyPartialMatch(String objName, String data) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, data};
	return verifyAction("verifypartialmatch", params);
    }
    public int verifySetText(String objName, String data) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, data};
	return verifyAction("verifysettext", params);
    }
    public int activateText(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("activatetext", params);
    }
    public int appendText(String objName, String data) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, data};
	return doAction("appendtext", params);
    }
    public int isTextStateEnabled(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("istextstateenabled", params);
    }
    public int getCharCount(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getInt("getcharcount", params);
    }
    public int setCursorPosition(String objName, int cursorPos) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, cursorPos};
	return doAction("setcursorposition", params);
    }
    public int getCursorPosition(String objName) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getInt("getcursorposition", params);
    }
    public int cutText(String objName, int startPos) throws LdtpExecutionError {
	return cutText(objName, startPos, -1);
    }
    public int cutText(String objName, int startPos, int endPos) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, startPos, endPos};
	return doAction("cuttext", params);
    }
    public int copyText(String objName, int startPos) throws LdtpExecutionError {
	return copyText(objName, startPos, -1);
    }
    public int copyText(String objName, int startPos, int endPos) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, startPos, endPos};
	return doAction("copytext", params);
    }
    public int deleteText(String objName, int startPos) throws LdtpExecutionError {
	return deleteText(objName, startPos, -1);
    }
    public int deleteText(String objName, int startPos, int endPos) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, startPos, endPos};
	return doAction("deletetext", params);
    }
    public int pasteText(String objName) throws LdtpExecutionError {
	return pasteText(objName, 0);
    }
    public int pasteText(String objName, int cursorPos) throws LdtpExecutionError {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, cursorPos};
	return doAction("pastetext", params);
    }
    public String getStatusBarText(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getString("getstatusbartext", params);
    }
    // Combo box
    public int unSelectItem(String objName, String itemName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, itemName};
	return doAction("unselectitem", params);
    }
    public int selectItem(String objName, String itemName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, itemName};
	return doAction("selectitem", params);
    }
    public int comboSelect(String objName, String itemName) {
	return selectItem(objName, itemName);
    }
    public int isChildSelected(String objName, String itemName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, itemName};
	return verifyAction("ischildselected", params);
    }
    public int verifySelect(String objName, String itemName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, itemName};
	return verifyAction("verifyselect", params);
    }
    public int isChildIndexSelected(String objName, int itemIndex) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, itemIndex};
	return verifyAction("ischildindexselected", params);
    }
    public int unSelectIndex(String objName, int itemIndex) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, itemIndex};
	return doAction("unselectindex", params);
    }
    public int selectIndex(String objName, int itemIndex) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, itemIndex};
	return doAction("selectindex", params);
    }
    public int comboSelectIndex(String objName, int itemIndex) {
	return selectIndex(objName, itemIndex);
    }
    public int selectedItemCount(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("selecteditemcount", params);
    }
    public int showList(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("showlist", params);
    }
    public int hideList(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("hidelist", params);
    }
    public int verifyDropDown(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifydropdown", params);
    }
    public int verifyShowList(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifyshowlist", params);
    }
    public int verifyHideList(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifyhidelist", params);
    }
    public String[] getAllItem(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getStringList("getallitem", params);
    }
    public int selectAll(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("selectall", params);
    }
    public int unSelectAll(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("unselectall", params);
    }
    // Mouse
    public int generateMouseEvent(int x, int y) {
	return generateMouseEvent(x, y, "b1p");
    }
    public int generateMouseEvent(int x, int y, String eventType) {
	Object[] params = new Object[]{x, y, eventType};
	return doAction("generatemouseevent", params);
    }
    public int mouseLeftClick(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("mouseleftclick", params);
    }
    public int mouseMove(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("mousemove", params);
    }
    public int mouseRightClick(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("mouserightclick", params);
    }
    public int doubleClick(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("doubleclick", params);
    }
    public int simulateMouseMove(int source_x, int source_y, int dest_x, int dest_y) {
	return simulateMouseMove(source_x, source_y, dest_x, dest_y, 0.0);
    }
    public int simulateMouseMove(int source_x, int source_y, int dest_x, int dest_y, double delay) {
	Object[] params = new Object[]{source_x, source_y, dest_x, dest_y, delay};
	return doAction("simulatemousemove", params);
    }
    // Page tab
    public int selectTab(String objName, String tabName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, tabName};
	return doAction("selecttab", params);
    }
    public int selectTabIndex(String objName, int tabIndex) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, tabIndex};
	return doAction("selecttabindex", params);
    }
    public int getTabCount(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("gettabcount", params);
    }
    public String getTabName(String objName, int tabIndex) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, tabIndex};
	return getString("gettabname", params);
    }
    public int verifyTabName(String objName, String tabName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, tabName};
	return verifyAction("verifytabname", params);
    }
    // Table
    public int getRowCount(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("getrowcount", params);
    }
    public int selectRow(String objName, String rowText) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowText};
	return doAction("selectrow", params);
    }
    public int selectRowPartialMatch(String objName, String rowText) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowText};
	return doAction("selectrowpartialmatch", params);
    }
    public int selectRowIndex(String objName, int rowIndex) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowIndex};
	return doAction("selectrowindex", params);
    }
    public int selectLastRow(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("selectlastrow", params);
    }
    public int setCellValue(String objName, int rowIndex) {
	return setCellValue(objName, rowIndex, 0, "");
    }
    public int setCellValue(String objName, int rowIndex, int column) {
	return setCellValue(objName, rowIndex, column, "");
    }
    public int setCellValue(String objName, int rowIndex, int column, String data) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowIndex, column, data};
	return doAction("setcellvalue", params);
    }
    public String getCellValue(String objName, int rowIndex) {
	return getCellValue(objName, rowIndex, 0);
    }
    public String getCellValue(String objName, int rowIndex, int column) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowIndex, column};
	return getString("getcellvalue", params);
    }
    public int rightClick(String objName, String rowText) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowText};
	return doAction("rightclick", params);
    }
    public int checkRow(String objName, int rowIndex) {
	return checkRow(objName, rowIndex, 0);
    }
    public int checkRow(String objName, int rowIndex, int column) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowIndex, column};
	return doAction("checkrow", params);
    }
    public int expandTableCell(String objName, int rowIndex) {
	return expandTableCell(objName, rowIndex, 0);
    }
    public int expandTableCell(String objName, int rowIndex, int column) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowIndex, column};
	return doAction("expandtablecell", params);
    }
    public int unCheckRow(String objName, int rowIndex) {
	return unCheckRow(objName, rowIndex, 0);
    }
    public int unCheckRow(String objName, int rowIndex, int column) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowIndex, column};
	return doAction("uncheckrow", params);
    }
    public int getTableRowIndex(String objName, String rowText) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowText};
	return getInt("gettablerowindex", params);
    }
    public int singleClickRow(String objName, String rowText) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowText};
	return getInt("singleclickrow", params);
    }
    public int doubleClickRow(String objName, String rowText) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowText};
	return getInt("doubleclickrow", params);
    }
    public int verifyTableCell(String objName, int rowIndex, int column, String rowText) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowIndex, column, rowText};
	return verifyAction("verifytablecell", params);
    }
    public int doesRowExist(String objName, String rowText) {
	return doesRowExist(objName, rowText, false);
    }
    public int doesRowExist(String objName, String rowText, Boolean partialMatch) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowText, partialMatch};
	return verifyAction("doesrowexist", params);
    }
    public int verifyPartialTableCell(String objName, int rowIndex, int column, String rowText) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowIndex, column, rowText};
	return verifyAction("verifypartialtablecell", params);
    }
    //
    public double getCellValue(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getDouble("getcellvalue", params);
    }
    public double getSliderValue(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getDouble("getslidervalue", params);
    }
    public int setCellValue(String objName, double rowValue) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowValue};
	return doAction("setcellvalue", params);
    }
    public int verifySetValue(String objName, double rowValue) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, rowValue};
	return verifyAction("verifysetvalue", params);
    }
    public double getMinValue(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getDouble("getminvalue", params);
    }
    public double getMaxValue(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getDouble("getmaxvalue", params);
    }
    public double getMax(String objName) {
	return getMaxValue(objName);
    }
    public double getMinIncrement(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getDouble("getminincrement", params);
    }
    public double getMaxIncrement(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return getDouble("getmaxincrement", params);
    }
    public int verifySliderVertical(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifyslidervertical", params);
    }
    public int verifySliderHorizontal(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifysliderhorizontal", params);
    }
    public int verifyScrollbarVertical(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifyscrollbarvertical", params);
    }
    public int verifyScrollbarHorizontal(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return verifyAction("verifyscrollbarhorizontal", params);
    }
    public int scrollUp(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("scrollup", params);
    }
    public int scrollDown(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("scrolldown", params);
    }
    public int scrollRight(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("scrollright", params);
    }
    public int scrollLeft(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("scrollleft", params);
    }
    public int setMax(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("setmax", params);
    }
    public int setMin(String objName) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName};
	return doAction("setmin", params);
    }
    public int increase(String objName, int iterations) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, iterations};
	return doAction("increase", params);
    }
    public int decrease(String objName, int iterations) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, iterations};
	return doAction("decrease", params);
    }
    public int oneUp(String objName, int iterations) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, iterations};
	return doAction("oneup", params);
    }
    public int oneDown(String objName, int iterations) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, iterations};
	return doAction("onedown", params);
    }
    public int oneRight(String objName, int iterations) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, iterations};
	return doAction("oneright", params);
    }
    public int oneLeft(String objName, int iterations) {
	if (windowName == null) {
	    throw new LdtpExecutionError("Window name missing");
	}
	Object[] params = new Object[]{windowName, objName, iterations};
	return doAction("oneleft", params);
    }
    // Image
    public String imageCapture(int y, int width, int height) {
	return imageCapture("", 0, y, width, height);
    }
    public String imageCapture(int width, int height) {
	return imageCapture("", 0, 0, width, height);
    }
    public String imageCapture(int height) {
	return imageCapture("", 0, 0, 0, height);
    }
    public String imageCapture() {
	return imageCapture("", 0, 0, 0, 0);
    }
    public String imageCapture(int x, int y, int width, int height) {
	return imageCapture("", x, y, width, height);
    }
    public String imageCapture(String windowName, int x, int y, int width, int height) {
	String data;
	Object[] params = new Object[]{windowName, x, y, width, height};
	String filename = null;
	try {
	    java.io.File f = java.io.File.createTempFile("ldtp_", ".png");
	    filename = f.getAbsolutePath();
	    f.delete();
	    data = getString("imagecapture", params);
	    Base64 base64 = new Base64();
	    FileOutputStream fp = new FileOutputStream(filename);
	    fp.write(base64.decodeBase64(data));
	    fp.close();
	} catch (java.io.FileNotFoundException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	} catch (java.io.IOException ex) {
	    throw new LdtpExecutionError(ex.getMessage());
	}
	return filename;
    }
    public static void main(String[] args) {
	int i;

	/*
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
