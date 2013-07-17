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
// This file depends on apache jar files:
// http://mirror.cc.columbia.edu/pub/software/apache//commons/codec/binaries/commons-codec-1.6-bin.zip
// http://www.apache.org/dyn/closer.cgi/ws/xmlrpc/
// Ran the test in Ubuntu 11.04 as
// export CLASSPATH=.:commons-codec-1.6.jar:ws-commons-utils-1.0.2.jar:xmlrpc-client-3.1.3.jar:xmlrpc-common-3.1.3.jar
// make
// make doc
// java Ldtp
// Ran the test in Windows 7 SP1 like: (Adjusted the code accordingly for Windows, as I need to maniuplate with Notepad)
// java -cp xmlrpc-client-3.1.3.jar;xmlrpc-common-3.1.3.jar;ws-commons-util-1.0.2.jar;commons-codec-1.6.jar;. Ldtp
import java.net.URL;
import java.util.Arrays;
import java.io.FileOutputStream;
import java.lang.ProcessBuilder;
import org.apache.commons.logging.Log; 
import org.apache.commons.logging.LogFactory; 
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.commons.codec.binary.Base64;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;

/**
 * Ldtp class is a wrapper to the Ldtp GUI automation library, works on both Windows and Linux environment
 */
public class Ldtp {
	Process p = null;
	boolean debug = false;
	String windowName = null;
	String serverAddr = null;
	String serverPort = null;
	ProcessBuilder pb;
	Boolean windowsEnv = false;
	XmlRpcClient client = null;
	PollEvents pollEvents = null;
	XmlRpcClientConfigImpl config = null;
	public Log log = LogFactory.getLog("");
	/**
	 * connectToServer (private), which connects to the running instance of LDTP server
	 */
	private void connectToServer() {
		if (serverAddr == null)
			serverAddr = System.getenv("LDTP_SERVER_ADDR");
		if (serverAddr == null)
			serverAddr = "localhost";
		if (serverPort == null)
			serverPort = System.getenv("LDTP_SERVER_PORT");
		if (serverPort == null)
			serverPort = "4118";
		if (System.getenv("LDTP_DEBUG") != null)
			debug = true;
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
		String url = String.format("http://%s:%s/RPC2", serverAddr, serverPort);
		try {
			config.setServerURL(new URL(url));
		} catch (java.net.MalformedURLException ex) {
			throw new LdtpExecutionError(ex.getMessage());
		}
		client = new XmlRpcClient();
		client.setConfig(config);
		Boolean alive = isAlive();
		if (!alive) {
			if (serverAddr.contains("localhost"))
				launchLdtpProcess();
			// Verify we are able to connect after launching the server
			alive = isAlive();
			if (!alive)
				throw new LdtpExecutionError("Unable to connect to server");
		}
	}
	/**
	 * isAlive (private) Check the connection to LDTP server
	 */
	private Boolean isAlive() {
		Boolean isAlive = false;
		Object[] params = null;
		try {
			isAlive = (Boolean)client.execute("isalive", params);
		} catch (org.apache.xmlrpc.XmlRpcException ex) {
			// Ignore any exception
		} catch (Exception ex) {
			// Ignore any exception
		}
		return isAlive;
	}
	/**
	 * launchLdtpProcess (private) Launch LDTP executable
	 */
	private void launchLdtpProcess() {
		if (windowsEnv)
			// Launch Windows LDTP
			pb = new ProcessBuilder("CobraWinLDTP.exe");
		else
			// Launch Linux LDTP
			pb = new ProcessBuilder("ldtp");
		try {
			// Start the process
			p = pb.start();
			// Add a hook to kill the process
			// started by current Ldtp instance
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
	/**
	 * terminateLdtpProcess (private) Terminate LDTP executable started by this instance
	 */
	private void terminateLdtpProcess() {
		if (p != null) {
			// Kill LDTP executable
			p.destroy();
		}
		if (pollEvents != null)
			pollEvents.pollServer = false;
	}
	/**
	 * Ldtp
	 *
	 * @param windowName Window to be manipulated
	 */
	public Ldtp(String windowName) {
		this(windowName, null);
	}
	/**
	 * Ldtp
	 *
	 * @param windowName Window to be manipulated
	 * @param serverAddr Server address to connect to
	 */
	public Ldtp(String windowName, String serverAddr) {
		this(windowName, serverAddr, null);
	}
	/**
	 * Ldtp
	 *
	 * @param windowName Window to be manipulated
	 * @param serverAddr Server address to connect to
	 * @param serverPort Server port to connect to
	 */
	public Ldtp(String windowName, String serverAddr, String serverPort) {
		if (windowName == null || windowName == "") {
			throw new LdtpExecutionError("Window name missing");
		}
		this.serverAddr = serverAddr;
		this.serverPort = serverPort;
		this.windowName = windowName;
		connectToServer();
		pollEvents = new PollEvents(this);
		pollEvents.start();
	}
	/**
	 * setWindowName Change window name
	 *
	 * @param windowName Window to be manipulated
	 */
	public void setWindowName(String windowName) {
		if (windowName == null || windowName == "") {
			throw new LdtpExecutionError("Window name missing");
		}
		this.windowName = windowName;
	}
	/**
	 * getWindowName Get currently set window name
	 */
	public String getWindowName() {
		return windowName;
	}
	/**
	 * getJavaObjectList Execute XML-RPC command and get the output as Java Object array
	 *
	 * @param cmd Command to be executed on the server side
	 * @param params Parameters to be passed to the command
	 * @return Return the output as Object array
	 */
	private Object[] getJavaObjectList(String cmd, Object[] params) {
		try {
			return (Object[])client.execute(cmd, params);
		} catch (org.apache.xmlrpc.XmlRpcException ex) {
			throw new LdtpExecutionError(ex.getMessage());
		}
	}
	/**
	 * verifyAction (private) Verification API
	 *
	 * @param cmd Command to be executed on the server side
	 * @param params Parameters to be passed to the command
	 * @return Return the output as 1 on success, 0 on failure
	 */
	private Integer verifyAction(String cmd, Object[] params) {
		try {
			return doAction(cmd, params);
		} catch (Exception ex) {
			return 0;
		}
	}
	/**
	 * verifyAction (private) Action API
	 *
	 * @param cmd Command to be executed on the server side
	 * @param params Parameters to be passed to the command
	 * @return Return the output as 1 on success, LdtpExecutionError exception on failure
	 */
	private Integer doAction(String cmd, Object[] params) {
		try {
			return (Integer)client.execute(cmd, params);
		} catch (org.apache.xmlrpc.XmlRpcException ex) {
			throw new LdtpExecutionError(ex.getMessage());
		}
	}
	/**
	 * getString (private) get String value as output
	 *
	 * @param cmd Command to be executed on the server side
	 * @param params Parameters to be passed to the command
	 * @return Return the output as String value on success
	 * @throws LdtpExecutionError exception on failure
	 */
	private String getString(String cmd, Object[] params) {
		try {
			return (String)client.execute(cmd, params);
		} catch (org.apache.xmlrpc.XmlRpcException ex) {
			throw new LdtpExecutionError(ex.getMessage());
		}
	}
	/**
	 * getInt (private) get Integer value as output
	 *
	 * @param cmd Command to be executed on the server side
	 * @param params Parameters to be passed to the command
	 * @return Return the output as Integer value on success
	 * @throws LdtpExecutionError exception on failure
	 */
	private Integer getInt(String cmd, Object[] params) {
		try {
			return (Integer)client.execute(cmd, params);
		} catch (org.apache.xmlrpc.XmlRpcException ex) {
			throw new LdtpExecutionError(ex.getMessage());
		}
	}
	/**
	 * getDouble (private) get Double value as output
	 *
	 * @param cmd Command to be executed on the server side
	 * @param params Parameters to be passed to the command
	 * @return Return the output as Double value on success
	 * @throws LdtpExecutionError exception on failure
	 */
	private Double getDouble(String cmd, Object[] params) {
		try {
			return (Double)client.execute(cmd, params);
		} catch (org.apache.xmlrpc.XmlRpcException ex) {
			throw new LdtpExecutionError(ex.getMessage());
		}
	}
	/**
	 * getDoubleList (private) Execute XML-RPC command and get the output as Double array
	 *
	 * @param cmd Command to be executed on the server side
	 * @param params Parameters to be passed to the command
	 * @return Return the output as Object array
	 */
	private Double[] getDoubleList(String cmd, Object[] params) {
		Double[] result = null;
		Object[] o = getJavaObjectList(cmd, params);
		result = Arrays.copyOf(o, o.length, Double[].class);
		return result;
	}
	/**
	 * getStringList (private) Execute XML-RPC command and get the output as String array
	 *
	 * @param cmd Command to be executed on the server side
	 * @param params Parameters to be passed to the command
	 * @return Return the output as String array
	 */
	private String[] getStringList(String cmd, Object[] params) {
		String[] result = null;
		Object[] o = getJavaObjectList(cmd, params);
		result = Arrays.copyOf(o, o.length, String[].class);
		return result;
	}
	/**
	 * getIntList (private) Execute XML-RPC command and get the output as Integer array
	 *
	 * @param cmd Command to be executed on the server side
	 * @param params Parameters to be passed to the command
	 * @return Return the output as Integer array
	 */
	private Integer[] getIntList(String cmd, Object[] params) {
		Integer[] result = null;
		Object[] o = getJavaObjectList(cmd, params);
		result = Arrays.copyOf(o, o.length, Integer[].class);
		return result;
	}
	// General
	/**
	 * getWindowList Get currently open window list
	 *
	 * @return Return the output as String array
	 */
	public String[] getWindowList() throws LdtpExecutionError {
		return getStringList("getwindowlist", null);
	}
	/**
	 * getAppList Get currently open application list
	 *
	 * @return Return the output as String array
	 */
	public String[] getAppList() throws LdtpExecutionError {
		return getStringList("getapplist", null);
	}
	/**
	 * getObjectList Get current windows object list
	 *
	 * @return Return the output as String array
	 */
	public String[] getObjectList() throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		return getStringList("getobjectlist", params);
	}
	/**
	 * getObjectInfo Get current object info
	 *
	 * @param objName Object name
	 * @return Return the properties of the current object as String array
	 */
	public String[] getObjectInfo(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getStringList("getobjectinfo", params);
	}
	/**
	 * getAccessKey Get access key
	 *
	 * @param objName Object name
	 * @return Return the access key as String
	 */
	public String getAccessKey(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getString("getaccesskey", params);
	}
	/**
	 * getObjectProperty Get current object property
	 *
	 * @param objName Object name
	 * @param property Property of the children like class, label, label_by, child_index
	 * @return Return the property as String
	 */
	public String getObjectProperty(String objName, String property) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, property};
		return getString("getobjectproperty", params);
	}
	/**
	 * getChild Get children matching child name
	 *
	 * @param childName Child name
	 * @return Return the children as String array
	 */
	public String[] getChild(String childName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, childName};
		return getStringList("getchild", params);
	}
	/**
	 * getChild Get children matching child name and role
	 *
	 * @param childName Child name
	 * @param role object role type
	 * @return Return the children as String array
	 */
	public String[] getChild(String childName, String role) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, childName, role};
		return getStringList("getchild", params);
	}
	/**
	 * getChild Get children matching child name, role, property
	 *
	 * @param childName Child name
	 * @param role object role type
	 * @param property property of child
	 * @return Return the children as String array
	 */
	public String[] getChild(String childName, String role, String property) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, childName, role, property};
		return getStringList("getchild", params);
	}
	/**
	 * getObjectSize Get object size
	 *
	 * @param objName Object name
	 * @return Return the size as Integer list
	 */
	public Integer[] getObjectSize(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getIntList("getobjectsize", params);
	}
	/**
	 * getWindowSize Get window size
	 *
	 * @return Return the size as Integer list
	 */
	public Integer[] getWindowSize() throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		return getIntList("getwindowsize", params);
	}
	/**
	 * reMap Re-Map current window
	 *
	 * @return Return the 1 on success
	 * @throws LdtpExecutionError exception on failure
	 */
	public int reMap() {
		Object[] params = new Object[]{windowName};
		return verifyAction("remap", params);
	}
	/**
	 * waitTime Sleep for 5 seconds
	 *
	 * @return Return the 1 on success
	 * @throws LdtpExecutionError exception on failure
	 */
	public int waitTime() {
		return waitTime(5);
	}
	/**
	 * waitTime Sleep for given seconds
	 *
	 * @param timeout Sleep for timeout seconds
	 * @return Return the 1 on success
	 * @throws LdtpExecutionError exception on failure
	 */
	public int waitTime(int timeout) {
		Object[] params = new Object[]{timeout};
		return doAction("wait", params);
	}
	/**
	 * objectTimeOut Change default object time out
	 *
	 * @param timeout Change default object time out search in seconds
	 * @return Return the 1 on success
	 * @throws LdtpExecutionError exception on failure
	 */
	public int objectTimeOut(int timeout) {
		Object[] params = new Object[]{timeout};
		return doAction("objecttimeout", params);
	}
	/**
	 * guiTimeOut Change default window time out search
	 *
	 * @param timeout Change default window time out search in seconds
	 * @return Return the 1 on success
	 * @throws LdtpExecutionError exception on failure
	 */
	public int guiTimeOut(int timeout) {
		Object[] params = new Object[]{timeout};
		return doAction("guitimeout", params);
	}
	/**
	 * getObjectNameAtCoords Get object name at co-ordinates without any delay
	 *
	 * @return Return String array of possible window name and object name
	 */
	public String[] getObjectNameAtCoords() {
		return getObjectNameAtCoords(0.0);
	}
	/**
	 * getObjectNameAtCoords Get object name at co-ordinates
	 *
	 * @param waitTime wait for the given time and then try to find the window and object name
	 * @return Return String array of possible window name and object name
	 */
	public String[] getObjectNameAtCoords(double waitTime) {
		Object[] params = new Object[]{waitTime};
		return getStringList("getobjectnameatcoords", params);
	}
	/**
	 * guiExist Verifies whether the current window exist or not
	 *
	 * @return Return 1 on success, 0 on failure
	 */
	public int guiExist() {
		return guiExist("");
	}
	/**
	 * guiExist Verifies whether the current window and given object exist or not
	 *
	 * @param objName Object name to look
	 * @return Return 1 on success, 0 on failure
	 */
	public int guiExist(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("guiexist", params);
	}
	/**
	 * waitTillGuiExist Wait for the current window for 30 seconds
	 *
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiExist() {
		return waitTillGuiExist("", 30, "");
	}
	/**
	 * waitTillGuiExist Wait for the current window and object name for 30 seconds
	 *
	 * @param objName Object name to look
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiExist(String objName) {
		return waitTillGuiExist(objName, 30, "");
	}
	/**
	 * waitTillGuiExist Wait for the current window and object name for given seconds
	 *
	 * @param objName Object name to look
	 * @param guiTimeOut Wait for the given time rather than default 30 seconds
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiExist(String objName, int guiTimeOut) {
		return waitTillGuiExist(objName, guiTimeOut, "");
	}
	/**
	 * waitTillGuiExist Wait for the current window for given seconds
	 *
	 * @param guiTimeOut Wait for the given time rather than default 30 seconds
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiExist(int guiTimeOut) {
		return waitTillGuiExist("", guiTimeOut, "");
	}
	/**
	 * waitTillGuiExist Wait for the current window, state for given seconds
	 *
	 * @param guiTimeOut Wait for the given time rather than default 30 seconds
	 * @param state Wait for the state
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiExist(int guiTimeOut, String state) {
		return waitTillGuiExist("", guiTimeOut, state);
	}
	/**
	 * waitTillGuiExist Wait for the current window, object name, state for given seconds
	 *
	 * @param objName Object name to look
	 * @param guiTimeOut Wait for the given time rather than default 30 seconds
	 * @param state Wait for the state
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiExist(String objName, int guiTimeOut, String state) {
		Object[] params = new Object[]{windowName, objName, guiTimeOut, state};
		return verifyAction("waittillguiexist", params);
	}
	/**
	 * waitTillGuiNotExist Wait for the current window to disappear for 30 seconds
	 *
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiNotExist() {
		return waitTillGuiNotExist("", 30, "");
	}
	/**
	 * waitTillGuiNotExist Wait for the current window, object name to disappear for 30 seconds
	 *
	 * @param objName Object name to look
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiNotExist(String objName) {
		return waitTillGuiNotExist(objName, 30, "");
	}
	/**
	 * waitTillGuiNotExist Wait for the current window, object name to disappear for given seconds
	 *
	 * @param objName Object name to look
	 * @param guiTimeOut Wait for the given time rather than default 30 seconds
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiNotExist(String objName, int guiTimeOut) {
		return waitTillGuiNotExist(objName, guiTimeOut, "");
	}
	/**
	 * waitTillGuiNotExist Wait for the current window to disappear for given seconds
	 *
	 * @param guiTimeOut Wait for the given time rather than default 30 seconds
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiNotExist(int guiTimeOut) {
		return waitTillGuiNotExist("", guiTimeOut, "");
	}
	/**
	 * waitTillGuiNotExist Wait for the current window, state to disapper for given seconds
	 *
	 * @param guiTimeOut Wait for the given time rather than default 30 seconds
	 * @param state Wait for the state
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiNotExist(int guiTimeOut, String state) {
		return waitTillGuiExist("", guiTimeOut, state);
	}
	/**
	 * waitTillGuiNotExist Wait for the current window, object name, state to disappear for given seconds
	 *
	 * @param objName Object name to look
	 * @param guiTimeOut Wait for the given time rather than default 30 seconds
	 * @param state Wait for the state
	 * @return Return 1 on success, 0 on failure
	 */
	public int waitTillGuiNotExist(String objName, int guiTimeOut, String state) {
		Object[] params = new Object[]{windowName, objName, guiTimeOut, state};
		return verifyAction("waittillguinotexist", params);
	}
	/**
	 * objectExist Verifies whether the window and object exist
	 *
	 * @param objName Object name to look
	 * @return Return 1 on success, 0 on failure
	 */
	public int objectExist(String objName) {
		return guiExist(objName);
	}
	/**
	 * delayCmdExec Delay each actions by given seconds
	 *
	 * @param delay Delay the command execution
	 * @return Return 1 on success, 0 on failure
	 */
	public int delayCmdExec(int delay) {
		Object[] params = new Object[]{delay};
		return verifyAction("delaycmdexec", params);
	}
	/**
	 * launchApp Launch application
	 *
	 * @param cmd Executable to launch
	 * @return Return pid of the launched process on success
	 * @throws LdtpExecutionError on failure
	 */
	public int launchApp(String cmd) {
		String[] args = {};
		return launchApp(cmd, args, 0, 1, "C");
	}
	/**
	 * launchApp Launch application
	 *
	 * @param cmd Executable to launch
	 * @param args String array argument to the executable
	 * @return Return pid of the launched process on success
	 * @throws LdtpExecutionError on failure
	 */
	public int launchApp(String cmd, String[] args) {
		return launchApp(cmd, args, 0, 1, "C");
	}
	/**
	 * launchApp Launch application
	 *
	 * @param cmd Executable to launch
	 * @param args String array argument to the executable
	 * @param delay Wait given number of seconds after the command executed successfully
	 * @return Return pid of the launched process on success
	 * @throws LdtpExecutionError on failure
	 */
	public int launchApp(String cmd, String[] args, int delay) {
		return launchApp(cmd, args, delay, 1, "C");
	}
	/**
	 * launchApp Launch application
	 *
	 * @param cmd Executable to launch
	 * @param args String array argument to the executable
	 * @param delay Wait given number of seconds after the command executed successfully
	 * @param env Gnome accessibility to be set or not
	 * @return Return pid of the launched process on success
	 * @throws LdtpExecutionError on failure
	 */
	public int launchApp(String cmd, String[] args, int delay, int env) {
		return launchApp(cmd, args, delay, env, "C");
	}
	/**
	 * launchApp Launch application
	 *
	 * @param cmd Executable to launch
	 * @param args String array argument to the executable
	 * @param delay Wait given number of seconds after the command executed successfully
	 * @param env Gnome accessibility to be set or not
	 * @param lang Locale language to be used
	 * @return Return pid of the launched process on success
	 * @throws LdtpExecutionError on failure
	 */
	public int launchApp(String cmd, String[] args, int delay, int env, String lang) {
		Object[] params = new Object[]{cmd, args, delay, env, lang};
		return doAction("launchapp", params);
	}
	/**
	 * pollEvents (private) Poll for events
	 *
	 * @return Return event generated on the server
	 */
	String pollEvents() {
		return getString("poll_events", null);
	}
	/**
	 * getLastLog Gets last log from server
	 *
	 * @return Return log from server
	 */
	public String getLastLog() {
		return getString("getlastlog", null);
	}
	/**
	 * startProcessMonitor Starts process monitor
	 *
	 * @param processName Process to be monitored
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int startProcessMonitor(String processName) throws LdtpExecutionError {
		Object[] params = new Object[]{processName};
		return doAction("startprocessmonitor", params);
	}
	/**
	 * stopProcessMonitor Stop process monitor
	 *
	 * @param processName Stop monitoring the process
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int stopProcessMonitor(String processName, int interval) throws LdtpExecutionError {
		Object[] params = new Object[]{processName, interval};
		return doAction("stopprocessmonitor", params);
	}
	/**
	 * getCpuStat Get CPU stat
	 *
	 * @param processName Get CPU stat of process
	 * @return Return Double list of CPU stat on success, empty list on failure
	 */
	public Double[] getCpuStat(String processName) {
		Object[] params = new Object[]{processName};
		return getDoubleList("getcpustat", params);
	}
	/**
	 * getMemoryStat Get memory stat
	 *
	 * @param processName Get memory stat of process
	 * @return Return Integer list of memory stat on success, empty list on failure
	 */
	public Integer[] getMemoryStat(String processName) {
		Object[] params = new Object[]{processName};
		return getIntList("getmemorystat", params);
	}
	/**
	 * windowUpTime Get uptime of window
	 *
	 * @return Return DateTime on success
	 * @throws LdtpExecutionError on failure
	 */
	// FIXME: Return DateTime, rather than int
	public int windowUpTime() throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		return doAction("windowuptime", params);
	}
	/**
	 * onWindowCreate On new window opened call the given method
	 *
	 * @param obj Class instance
	 * @param isStatic Passed method name is static ?
	 * @param methodName Method name to be called from the class
	 * @param args Optional arguments to the callback method
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int onWindowCreate(Object obj, final boolean isStatic, final String methodName, final Object... args) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		pollEvents.addCallbacks("onwindowcreate-" + windowName, obj, isStatic, methodName, args);
		return doAction("onwindowcreate", params);
	}
	/**
	 * removeCallback Remove window name from callback method
	 *
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int removeCallback() throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		pollEvents.removeCallbacks("onwindowcreate-" + windowName);
		return doAction("removecallback", params);
	}
	/**
	 * registerEvent Register event to watch for
	 *
	 * @param eventName Event name to watch for
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int registerEvent(String eventName) throws LdtpExecutionError {
		Object[] params = new Object[]{eventName};
		return doAction("registerevent", params);
	}
	/**
	 * deRegisterEvent De-Register event to watch for
	 *
	 * @param eventName Don't watch the event name
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int deRegisterEvent(String eventName) throws LdtpExecutionError {
		Object[] params = new Object[]{eventName};
		return doAction("deRegisterevent", params);
	}
	/**
	 * registerKbEvent register Keyboard event to watch for
	 *
	 * @param keys Watch the keys
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int registerKbEvent(String keys) throws LdtpExecutionError {
		Object[] params = new Object[]{keys};
		return doAction("registerevent", params);
	}
	/**
	 * registerKbEvent register Keyboard event to watch for
	 *
	 * @param keys Watch the keys
	 * @param modifiers Keyboard modifiers
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int registerKbEvent(String keys, int modifiers) throws LdtpExecutionError {
		Object[] params = new Object[]{keys, modifiers};
		return doAction("registerevent", params);
	}
	/**
	 * deRegisterKbEvent De-Register Keyboard event to watch for
	 *
	 * @param keys Don't watch the keys
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int deRegisterKbEvent(String keys) throws LdtpExecutionError {
		Object[] params = new Object[]{keys};
		return doAction("deregisterevent", params);
	}
	/**
	 * deRegisterKbEvent De-Register Keyboard event to watch for
	 *
	 * @param keys Don't watch the keys
	 * @param modifiers Keyboard modifiers
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int deRegisterKbEvent(String keys, int modifiers) throws LdtpExecutionError {
		Object[] params = new Object[]{keys, modifiers};
		return doAction("deregisterevent", params);
	}
	/**
	 * maximizeWindow Maximize all windows that are currently open
	 *
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int maximizeWindow() throws LdtpExecutionError {
		return doAction("maximizewindow", null);
	}
	/**
	 * maximizeWindow Maximize given window that is currently open
	 *
	 * @param windowName Maximize given window name
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int maximizeWindow(String windowName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		return doAction("maximizewindow", params);
	}
	/**
	 * minimizeWindow Minimize all window that are currently open
	 *
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int minimizeWindow() throws LdtpExecutionError {
		return doAction("minimizewindow", null);
	}
	/**
	 * minimizeWindow Minimize given window that is currently open
	 *
	 * @param windowName Minimize given window name
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int minimizeWindow(String windowName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		return doAction("minimizewindow", params);
	}
	/**
	 * closeWindow Close all window that are currently open
	 *
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int closeWindow() throws LdtpExecutionError {
		return doAction("closewindow", null);
	}
	/**
	 * closeWindow Close given window that is currently open
	 *
	 * @param windowName Close given window name
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int closeWindow(String windowName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		return doAction("closewindow", params);
	}
	/**
	 * unMaximizeWindow Un-maximize all windows
	 *
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unMaximizeWindow() throws LdtpExecutionError {
		return doAction("unmaximizewindow", null);
	}
	/**
	 * unMaximizeWindow Un-maximize given window that is currently open
	 *
	 * @param windowName Un-maximize given window name
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unMaximizeWindow(String windowName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		return doAction("unmaximizewindow", params);
	}
	/**
	 * unMinimizeWindow Un-minize all windows
	 *
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unMinimizeWindow() throws LdtpExecutionError {
		return doAction("unminimizewindow", null);
	}
	/**
	 * unMinimizeWindow Un-minize given window
	 *
	 * @param windowName unMinimize given window name
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unMinimizeWindow(String windowName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		return doAction("unminimizewindow", params);
	}
	/**
	 * activateWindow Activate given window that is currently open
	 *
	 * @param windowName Activate given window name
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int activateWindow(String windowName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName};
		return doAction("activatewindow", params);
	}
	/**
	 * appUnderTest Application under test
	 */
	public int appUnderTest(String appName) {
		Object[] params = new Object[]{appName};
		return doAction("appundertest", params);
	}
	/**
	 * getAllStates Get all states of given object
	 *
	 * @return Return String array of states on success
	 * @throws LdtpExecutionError on failure
	 */
	public String[] getAllStates(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getStringList("getallstates", params);
	}
	/**
	 * hasState Verifies whether the object has given state
	 *
	 * @param objName Object name inside the window
	 * @param state State of the object to be verified
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int hasState(String objName, String state) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, state};
		return verifyAction("hasstate", params);
	}
	/**
	 * hasState Verifies whether the object has given state
	 *
	 * @param objName Object name inside the window
	 * @param state State of the object to be verified
	 * @param guiTimeOut Wait for the state till timeout
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int hasState(String objName, String state, int guiTimeOut) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, state, guiTimeOut};
		return verifyAction("hasstate", params);
	}
	/**
	 * grabFocus Grabs focus of given object name
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int grabFocus(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("grabfocus", params);
	}
	/**
	 * click Clicks on the object inside the window
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int click(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("click", params);
	}
	/**
	 * press Press the object
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int press(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("press", params);
	}
	/**
	 * check Check marks the check box
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int check(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("check", params);
	}
	/**
	 * unCheck Un-check check box
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unCheck(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("uncheck", params);
	}
	/**
	 * verifyToggled Verify whether the toggle button is toggled
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyToggled(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifytoggled", params);
	}
	/**
	 * verifyCheck Verify whether the check box is checked
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyCheck(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifycheck", params);
	}
	/**
	 * verifyUnCheck Verify whether the check box is un-checked
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyUnCheck(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifyuncheck", params);
	}
	/**
	 * stateEnabled Verify whether the object state is enabled
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success, 0 on failure
	 */
	public int stateEnabled(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("stateenabled", params);
	}
	/**
	 * verifyPushButton Verify whether the given object is push button
	 *
	 * @param objName Object name inside the window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyPushButton(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifyPushButton", params);
	}
	/**
	 * getPanelChildCount Get child count of a panel
	 *
	 * @param objName Object name inside the window
	 * @return Return child count on success, -1 on failure
	 */
	public int getPanelChildCount(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return getInt("getpanelchildcount", params);
	}
	/**
	 * selectPanel Select panel by index
	 *
	 * @param objName Object name inside the window
	 * @param index Index in panel
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectPanel(String objName, int index) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, index};
		return doAction("selectpanel", params);
	}
	/**
	 * selectPanelIndex Select panel by index
	 *
	 * @param objName Object name inside the window
	 * @param index Index in panel
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectPanelIndex(String objName, int index) throws LdtpExecutionError {
		return selectPanel(objName, index);
	}
	/**
	 * selectPanelName Select panel by name
	 *
	 * @param objName Object name inside the window
	 * @param name Child name under panel
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectPanelName(String objName, String name) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, name};
		return doAction("selectpanelname", params);
	}
	// Menu
	/**
	 * selectMenuItem Select given menu item
	 *
	 * @param objName Object name inside the window, should be ; separated
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectMenuItem(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("selectmenuitem", params);
	}
	/**
	 * doesMenuItemExist Verifies whether the given menu item is enabled or not
	 *
	 * @param objName Object name inside the window, should be ; separated
	 * @return Return 1 on success, 0 on failure
	 */
	public int doesMenuItemExist(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("doesmenuitemexist", params);
	}
	/**
	 * listSubMenus Lists all the submenu items
	 *
	 * @param objName Object name inside the window, should be ; separated
	 * @return Return sub menus as String array on success
	 * @throws LdtpExecutionError on failure
	 */
	public String[] listSubMenus(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getStringList("listsubmenus", params);
	}
	/**
	 * menuCheck Checks the menuitem
	 *
	 * @param objName Object name inside the window, should be ; separated
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int menuCheck(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("menucheck", params);
	}
	/**
	 * menuUnCheck Un-checks the menuitem
	 *
	 * @param objName Object name inside the window, should be ; separated
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int menuUnCheck(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("menuuncheck", params);
	}
	/**
	 * menuItemEnabled Verifies whether the menuitem is enabled
	 *
	 * @param objName Object name inside the window, should be ; separated
	 * @return Return 1 on success, 0 on failure
	 */
	public int menuItemEnabled(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("menuitemenabled", params);
	}
	/**
	 * verifyMenuCheck Verifies whether the menuitem is checked
	 *
	 * @param objName Object name inside the window, should be ; separated
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyMenuCheck(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifymenucheck", params);
	}
	/**
	 * verifyMenuUnCheck Verifies whether the menuitem is un-checked
	 *
	 * @param objName Object name inside the window, should be ; separated
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyMenuUnCheck(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifymenuuncheck", params);
	}
	/**
	 * invokeMenu Invokes menu item that are on Linux system tray
	 *
	 * @param objName Object name inside the window, should be ; separated
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int invokeMenu(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("invokemenu", params);
	}
	// Text
	/**
	 * generateKeyEvent Generate keyboard event
	 *
	 * @param data Input string
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int generateKeyEvent(String data) throws LdtpExecutionError {
		Object[] params = new Object[]{data};
		return doAction("generatekeyevent", params);
	}
	/**
	 * keyPress Presses keyboard input
	 *
	 * @param data Input string
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int keyPress(String data) throws LdtpExecutionError {
		Object[] params = new Object[]{data};
		return doAction("keypress", params);
	}
	/**
	 * keyRelease Releases keyboard input
	 *
	 * @param data Input string
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int keyRelease(String data) throws LdtpExecutionError {
		Object[] params = new Object[]{data};
		return doAction("keyrelease", params);
	}
	/**
	 * enterString Generates keyboard input on the current focused window
	 *
	 * @param data Input string
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int enterString(String data) throws LdtpExecutionError {
		Object[] params = new Object[]{data};
		return doAction("enterstring", params);
	}
	/**
	 * enterString Generates keyboard input
	 *
	 * @param objName Object name inside the current window
	 * @param data Input string
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int enterString(String objName, String data) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, data};
		return doAction("enterstring", params);
	}
	/**
	 * setTextValue Sets text value
	 *
	 * @param objName Object name inside the current window
	 * @param data Input string
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int setTextValue(String objName, String data) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, data};
		return doAction("settextvalue", params);
	}
	/**
	 * getTextValue Gets text value
	 *
	 * @param objName Object name inside the current window
	 * @return Return data as String on success
	 * @throws LdtpExecutionError on failure
	 */
	public String getTextValue(String objName) throws LdtpExecutionError {
		return getTextValue(objName, 0, 0);
	}
	/**
	 * getTextValue Gets text value
	 *
	 * @param objName Object name inside the current window
	 * @param startPos Start position to get the text
	 * @return Return data as String on success
	 * @throws LdtpExecutionError on failure
	 */
	public String getTextValue(String objName, int startPos) throws LdtpExecutionError {
		return getTextValue(objName, startPos, 0);
	}
	/**
	 * getTextValue Gets text value
	 *
	 * @param objName Object name inside the current window
	 * @param startPos Start position to get the text
	 * @param endPos End position to get the text
	 * @return Return data as String on success
	 * @throws LdtpExecutionError on failure
	 */
	public String getTextValue(String objName, int startPos, int endPos) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, startPos, endPos};
		return getString("gettextvalue", params);
	}
	/**
	 * verifyPartialMatch Verify text with partial string
	 *
	 * @param objName Object name inside the current window
	 * @param data Text to be verified
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyPartialMatch(String objName, String data) {
		Object[] params = new Object[]{windowName, objName, data};
		return verifyAction("verifypartialmatch", params);
	}
	/**
	 * verifySetText Verifies complete text is available in the text field
	 *
	 * @param objName Object name inside the current window
	 * @param data Text to be verified
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifySetText(String objName, String data) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, data};
		return verifyAction("verifysettext", params);
	}
	/**
	 * activateText Activates text area for focus
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int activateText(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("activatetext", params);
	}
	/**
	 * appendText Appends given text to existing text
	 *
	 * @param objName Object name inside the current window
	 * @param data Input string
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int appendText(String objName, String data) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, data};
		return doAction("appendtext", params);
	}
	/**
	 * isTextStateEnabled Verifies whether text field is enabled or not
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success, 0 on failure
	 */
	public int isTextStateEnabled(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("istextstateenabled", params);
	}
	/**
	 * getCharCount Get character count of a text field
	 *
	 * @param objName Object name inside the current window
	 * @return Return character count as Integer on success
	 * @throws LdtpExecutionError on failure
	 */
	public int getCharCount(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getInt("getcharcount", params);
	}
	/**
	 * setCursorPosition Moves the cursor position
	 *
	 * @param objName Object name inside the current window
	 * @param cursorPos New cursor position
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int setCursorPosition(String objName, int cursorPos) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, cursorPos};
		return doAction("setcursorposition", params);
	}
	/**
	 * getCursorPosition Gets the current cursor position
	 *
	 * @param objName Object name inside the current window
	 * @return Return cursor position as Integer value on success, -1 on failure
	 */
	public int getCursorPosition(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return getInt("getcursorposition", params);
	}
	/**
	 * cutText Cut the text and copy to clipboard
	 *
	 * @param objName Object name inside the current window
	 * @param startPos Start position from where to cut the text
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int cutText(String objName, int startPos) throws LdtpExecutionError {
		return cutText(objName, startPos, -1);
	}
	/**
	 * cutText Cut the text and copy to clipboard
	 *
	 * @param objName Object name inside the current window
	 * @param startPos Start position from where to cut the text
	 * @param endPos End position of text to be cut
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int cutText(String objName, int startPos, int endPos) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, startPos, endPos};
		return doAction("cuttext", params);
	}
	/**
	 * copyText Copy the text to clipboard
	 *
	 * @param objName Object name inside the current window
	 * @param startPos Start position from where to copy the text
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int copyText(String objName, int startPos) throws LdtpExecutionError {
		return copyText(objName, startPos, -1);
	}
	/**
	 * copyText Copy the text to clipboard
	 *
	 * @param objName Object name inside the current window
	 * @param startPos Start position from where to copy the text
	 * @param endPos End position to which the text has to be copied
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int copyText(String objName, int startPos, int endPos) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, startPos, endPos};
		return doAction("copytext", params);
	}
	/**
	 * deleteText Delete the text
	 *
	 * @param objName Object name inside the current window
	 * @param startPos Start position from where to delete the text
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int deleteText(String objName, int startPos) throws LdtpExecutionError {
		return deleteText(objName, startPos, -1);
	}
	/**
	 * deleteText Delete the text
	 *
	 * @param objName Object name inside the current window
	 * @param startPos Start position from where to delete the text
	 * @param endPos End position to which the text has to be deleted
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int deleteText(String objName, int startPos, int endPos) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, startPos, endPos};
		return doAction("deletetext", params);
	}
	/**
	 * pasteText Paste the text from clipboard
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int pasteText(String objName) throws LdtpExecutionError {
		return pasteText(objName, 0);
	}
	/**
	 * pasteText Paste the text from clipboard
	 *
	 * @param objName Object name inside the current window
	 * @param cursorPos Cursor position in which the text has to be pasted
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int pasteText(String objName, int cursorPos) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, cursorPos};
		return doAction("pastetext", params);
	}
	/**
	 * pasteText Paste the text from clipboard
	 *
	 * @param objName Object name inside the current window
	 * @return Return status bar text as String on success
	 * @throws LdtpExecutionError on failure
	 */
	public String getStatusBarText(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getString("getstatusbartext", params);
	}
	// Combo box
	/**
	 * unSelectItem Unselect item in combo box
	 *
	 * @param objName Object name inside the current window
	 * @param itemName item name to be unselected
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unSelectItem(String objName, String itemName) {
		Object[] params = new Object[]{windowName, objName, itemName};
		return doAction("unselectitem", params);
	}
	/**
	 * selectItem Select item in combo box
	 *
	 * @param objName Object name inside the current window
	 * @param itemName item name to be selected
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectItem(String objName, String itemName) {
		Object[] params = new Object[]{windowName, objName, itemName};
		return doAction("selectitem", params);
	}
	/**
	 * comboSelect Select item in combo box
	 *
	 * @param objName Object name inside the current window
	 * @param itemName item name to be selected
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int comboSelect(String objName, String itemName) throws LdtpExecutionError {
		return selectItem(objName, itemName);
	}
	/**
	 * isChildSelected Is child selected in combobox
	 *
	 * @param objName Object name inside the current window
	 * @param itemName item name to be verified
	 * @return Return 1 on success, 0 on failure
	 */
	public int isChildSelected(String objName, String itemName) {
		Object[] params = new Object[]{windowName, objName, itemName};
		return verifyAction("ischildselected", params);
	}
	/**
	 * verifySelect Verify text is selected in combobox
	 *
	 * @param objName Object name inside the current window
	 * @param itemName item name to be verified
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifySelect(String objName, String itemName) {
		Object[] params = new Object[]{windowName, objName, itemName};
		return verifyAction("verifyselect", params);
	}
	/**
	 * isChildIndexSelected Is child index selected in combobox
	 *
	 * @param objName Object name inside the current window
	 * @param itemIndex item index to be verified
	 * @return Return 1 on success, 0 on failure
	 */
	public int isChildIndexSelected(String objName, int itemIndex) {
		Object[] params = new Object[]{windowName, objName, itemIndex};
		return verifyAction("ischildindexselected", params);
	}
	/**
	 * unSelectIndex Unselect given index from the combo box selection list
	 *
	 * @param objName Object name inside the current window
	 * @param itemIndex item index to be unselected
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unSelectIndex(String objName, int itemIndex) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, itemIndex};
		return doAction("unselectindex", params);
	}
	/**
	 * selectIndex Select given index in the combo box
	 *
	 * @param objName Object name inside the current window
	 * @param itemIndex item index to be selected
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectIndex(String objName, int itemIndex) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, itemIndex};
		return doAction("selectindex", params);
	}
	/**
	 * comboSelectIndex Select given index in the combo box
	 *
	 * @param objName Object name inside the current window
	 * @param itemIndex item index to be selected
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int comboSelectIndex(String objName, int itemIndex) throws LdtpExecutionError {
		return selectIndex(objName, itemIndex);
	}
	/**
	 * selectedItemCount Get number of items selected in combo box
	 *
	 * @param objName Object name inside the current window
	 * @return Return number of items selected on success, -1 on failure
	 */
	public int selectedItemCount(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return doAction("selecteditemcount", params);
	}
	/**
	 * getComboValue Get combobox value
	 *
	 * @param objName Object name inside the current window
	 * @return Return combobox value on success
	 * @throws LdtpExecutionError on failure
	 */
	public String getComboValue(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getString("getcombovalue", params);
	}
	/**
	 * showList Show combo box entries
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int showList(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("showlist", params);
	}
	/**
	 * hideList Hide combo box entries
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int hideList(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("hidelist", params);
	}
	/**
	 * verifyDropDown Verify drop down is shown
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyDropDown(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifydropdown", params);
	}
	/**
	 * verifyShowList Verify combo box list is displayed
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyShowList(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifyshowlist", params);
	}
	/**
	 * verifyHideList Verify combo box list is closed
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyHideList(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifyhidelist", params);
	}
	/**
	 * getAllItem Gets all item from combo box
	 *
	 * @param objName Object name inside the current window
	 * @return Return String array on success
	 * @throws LdtpExecutionError on failure
	 */
	public String[] getAllItem(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getStringList("getallitem", params);
	}
	/**
	 * selectAll Select all the item in combo box
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectAll(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return doAction("selectall", params);
	}
	/**
	 * unSelectAll Un-select all the item in combo box
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unSelectAll(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return doAction("unselectall", params);
	}
	// Mouse
	/**
	 * generateMouseEvent Generate mouse event
	 *
	 * @param x X co-ordinate
	 * @param y Y co-ordinate
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int generateMouseEvent(int x, int y) throws LdtpExecutionError {
		return generateMouseEvent(x, y, "b1p");
	}
	/**
	 * generateMouseEvent Generate mouse event
	 *
	 * @param x X co-ordinate
	 * @param y Y co-ordinate
	 * @param eventType Event type to be generated
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int generateMouseEvent(int x, int y, String eventType) {
		Object[] params = new Object[]{x, y, eventType};
		return doAction("generatemouseevent", params);
	}
	/**
	 * mouseLeftClick Generate mouse left click on the object
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int mouseLeftClick(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("mouseleftclick", params);
	}
	/**
	 * doubleClick Generate double click on the object
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int doubleClick(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("doubleclick", params);
	}
	/**
	 * mouseMove Move mouse to the object
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int mouseMove(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return doAction("mousemove", params);
	}
	/**
	 * mouseRightClick Generate mouse right click on the object
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int mouseRightClick(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return doAction("mouserightclick", params);
	}
	/**
	 * simulateMouseMove Simulate mouse move from source to destination
	 *
	 * @param source_x Source X co-ordinate
	 * @param source_y Source Y co-ordinate
	 * @param dest_x Destination X co-ordinate
	 * @param dest_y Destination Y co-ordinate
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int simulateMouseMove(int source_x, int source_y, int dest_x, int dest_y) {
		return simulateMouseMove(source_x, source_y, dest_x, dest_y, 0.0);
	}
	/**
	 * simulateMouseMove Simulate mouse move from source to destination
	 *
	 * @param source_x Source X co-ordinate
	 * @param source_y Source Y co-ordinate
	 * @param dest_x Destination X co-ordinate
	 * @param dest_y Destination Y co-ordinate
	 * @param delay Delay between each pixel move in seconds
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int simulateMouseMove(int source_x, int source_y, int dest_x, int dest_y, double delay) {
		Object[] params = new Object[]{source_x, source_y, dest_x, dest_y, delay};
		return doAction("simulatemousemove", params);
	}
	// Page tab
	/**
	 * selectTab Select tab based on the given name
	 *
	 * @param objName Object name inside the current window
	 * @param tabName Tab name to be selected
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectTab(String objName, String tabName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, tabName};
		return doAction("selecttab", params);
	}
	/**
	 * selectTabIndex Select tab based on the given index
	 *
	 * @param objName Object name inside the current window
	 * @param tabIndex Tab index to be selected
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectTabIndex(String objName, int tabIndex) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, tabIndex};
		return doAction("selecttabindex", params);
	}
	/**
	 * getTabCount Get number of tabs currently opened
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int getTabCount(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("gettabcount", params);
	}
	/**
	 * getTabName Get tab name based on given index
	 *
	 * @param objName Object name inside the current window
	 * @param tabIndex Tab index to get
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public String getTabName(String objName, int tabIndex) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, tabIndex};
		return getString("gettabname", params);
	}
	/**
	 * verifyTabName Verify tab name is correct
	 *
	 * @param objName Object name inside the current window
	 * @param tabName Tab name to be verified
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyTabName(String objName, String tabName) {
		Object[] params = new Object[]{windowName, objName, tabName};
		return verifyAction("verifytabname", params);
	}
	// Table
	/**
	 * getRowCount Get table cell row count
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int getRowCount(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("getrowcount", params);
	}
	/**
	 * selectRow Select table cell with row text matching
	 *
	 * @param objName Object name inside the current window
	 * @param rowText Row text to be matched
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectRow(String objName, String rowText) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowText, false};
		return doAction("selectrow", params);
	}
	/**
	 * selectRowPartialMatch Select table cell with partial row text matching
	 *
	 * @param objName Object name inside the current window
	 * @param rowText Row text to be matched
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectRowPartialMatch(String objName, String rowText) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowText};
		return doAction("selectrowpartialmatch", params);
	}
	/**
	 * selectRowIndex Select table cell based on index
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index to be selected
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectRowIndex(String objName, int rowIndex) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowIndex};
		return doAction("selectrowindex", params);
	}
	/**
	 * selectLastRow Select last table cell in the table
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int selectLastRow(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("selectlastrow", params);
	}
	/**
	 * setCellValue Set cell value with the given data on row index
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index in which data has to be set
	 * @param data Data to be set
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int setCellValue(String objName, int rowIndex, String data) throws LdtpExecutionError {
		return setCellValue(objName, rowIndex, 0, data);
	}
	/**
	 * setCellValue Set cell value with the given data on row index and column
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index in which data has to be set
	 * @param column Column in which data has to be set
	 * @param data Data to be set
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int setCellValue(String objName, int rowIndex, int column, String data) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowIndex, column, data};
		return doAction("setcellvalue", params);
	}
	/**
	 * getCellValue Gets cell value from row index and column 0
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index in which data has to be get
	 * @return Return data from cell as String on success
	 * @throws LdtpExecutionError on failure
	 */
	public String getCellValue(String objName, int rowIndex) throws LdtpExecutionError {
		return getCellValue(objName, rowIndex, 0);
	}
	/**
	 * getCellValue Gets cell value from row index and column
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index in which data has to be get
	 * @param column Column in which data has to be get
	 * @return Return data from cell as String on success
	 * @throws LdtpExecutionError on failure
	 */
	public String getCellValue(String objName, int rowIndex, int column) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowIndex, column};
		return getString("getcellvalue", params);
	}
	/**
	 * getCellSize Gets cell size from row index and column 0
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index in which data has to be get
	 * @return Return size of cell as Integer array on success
	 * @throws LdtpExecutionError on failure
	 */
	public Integer[] getCellSize(String objName, int rowIndex) throws LdtpExecutionError {
		return getCellSize(objName, rowIndex, 0);
	}
	/**
	 * getCellSize Gets cell value from row index and column
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index in which data has to be get
	 * @param column Column in which data has to be get
	 * @return Return size of cell as Integer array on success
	 * @throws LdtpExecutionError on failure
	 */
	public Integer[] getCellSize(String objName, int rowIndex, int column) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowIndex, column};
		return getIntList("getcellsize", params);
	}
	/**
	 * rightClick Right click on table cell with matching row text
	 *
	 * @param objName Object name inside the current window
	 * @param rowText Row text to be matched
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int rightClick(String objName, String rowText) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowText};
		return doAction("rightclick", params);
	}
	/**
	 * doubleClickRow Double click on table cell with matching row text
	 *
	 * @param objName Object name inside the current window
	 * @param rowText Row text to be matched
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int doubleClickRow(String objName, String rowText) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowText};
		return doAction("doubleclickrow", params);
	}
	/**
	 * checkRow Checkbox the table cell based on row index and column 0
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index to be checked
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int checkRow(String objName, int rowIndex) throws LdtpExecutionError {
		return checkRow(objName, rowIndex, 0);
	}
	/**
	 * checkRow Checkbox the table cell based on row index
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index to be checked
	 * @param column Column index to be checked
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int checkRow(String objName, int rowIndex, int column) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowIndex, column};
		return doAction("checkrow", params);
	}
	/**
	 * expandTableCell Expand table cell based on row index and column 0
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index to be expanded
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int expandTableCell(String objName, int rowIndex) throws LdtpExecutionError {
		return expandTableCell(objName, rowIndex, 0);
	}
	/**
	 * expandTableCell Expand table cell based on row index and column
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index to be expanded
	 * @param column Column index to be expanded
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int expandTableCell(String objName, int rowIndex, int column) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowIndex, column};
		return doAction("expandtablecell", params);
	}
	/**
	 * unCheckRow Un-Checkbox the table cell based on row index and column 0
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index to be checked
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unCheckRow(String objName, int rowIndex) throws LdtpExecutionError {
		return unCheckRow(objName, rowIndex, 0);
	}
	/**
	 * unCheckRow Un-Checkbox the table cell based on row index and column
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index to be checked
	 * @param column Column index to be checked
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int unCheckRow(String objName, int rowIndex, int column) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowIndex, column};
		return doAction("uncheckrow", params);
	}
	/**
	 * getTableRowIndex Get table row index based on row text
	 *
	 * @param objName Object name inside the current window
	 * @param rowText Row text to search for
	 * @return Return row index as Integer on success
	 * @throws LdtpExecutionError on failure
	 */
	public int getTableRowIndex(String objName, String rowText) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowText};
		return getInt("gettablerowindex", params);
	}
	/**
	 * singleClickRow Single click on table cell row based on row text
	 *
	 * @param objName Object name inside the current window
	 * @param rowText Row text to search for
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int singleClickRow(String objName, String rowText) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, rowText};
		return getInt("singleclickrow", params);
	}
	/**
	 * verifyTableCell Verify table cell text
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index to be verified
	 * @param column Column index to be verified
	 * @param rowText Row text to search for
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyTableCell(String objName, int rowIndex, int column, String rowText) {
		Object[] params = new Object[]{windowName, objName, rowIndex, column, rowText};
		return verifyAction("verifytablecell", params);
	}
	/**
	 * doesRowExist Check whether a row exist with the given text
	 *
	 * @param objName Object name inside the current window
	 * @param rowText Row text to search for
	 * @return Return 1 on success, 0 on failure
	 */
	public int doesRowExist(String objName, String rowText) {
		return doesRowExist(objName, rowText, false);
	}
	/**
	 * doesRowExist Check whether a row exist with the given partial text
	 *
	 * @param objName Object name inside the current window
	 * @param rowText Row text to search for
	 * @param partialMatch Verify partial match
	 * @return Return 1 on success, 0 on failure
	 */
	public int doesRowExist(String objName, String rowText, Boolean partialMatch) {
		Object[] params = new Object[]{windowName, objName, rowText, partialMatch};
		return verifyAction("doesrowexist", params);
	}
	/**
	 * verifyPartialTableCell Verify table cell with partial text
	 *
	 * @param objName Object name inside the current window
	 * @param rowIndex Row index to be verified
	 * @param column Column index to be verified
	 * @param rowText Partial row text to search for
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyPartialTableCell(String objName, int rowIndex, int column, String rowText) {
		Object[] params = new Object[]{windowName, objName, rowIndex, column, rowText};
		return verifyAction("verifypartialtablecell", params);
	}
	// Scrollbar / slider
	/**
	 * getValue Get value from spin button
	 *
	 * @param objName Object name inside the current window
	 * @return Return Double value on success
	 * @throws LdtpExecutionError on failure
	 */
	public double getValue(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getDouble("getcellvalue", params);
	}
	/**
	 * getSliderValue Get value from slider
	 *
	 * @param objName Object name inside the current window
	 * @return Return Double value on success
	 * @throws LdtpExecutionError on failure
	 */
	public double getSliderValue(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getDouble("getslidervalue", params);
	}
	/**
	 * setValue Set value with given double value
	 *
	 * @param objName Object name inside the current window
	 * @param value to be set
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int setValue(String objName, double value) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, value};
		return doAction("setcellvalue", params);
	}
	/**
	 * verifySetValue Verify whether the value set is correct
	 *
	 * @param objName Object name inside the current window
	 * @param rowValue Row value to be verified
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifySetValue(String objName, double rowValue) {
		Object[] params = new Object[]{windowName, objName, rowValue};
		return verifyAction("verifysetvalue", params);
	}
	/**
	 * getMinValue Get minimum slider value
	 *
	 * @param objName Object name inside the current window
	 * @return Return minimum Double value on success
	 * @throws LdtpExecutionError on failure
	 */
	public double getMinValue(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getDouble("getminvalue", params);
	}
	/**
	 * getMaxValue Get maximum slider value
	 *
	 * @param objName Object name inside the current window
	 * @return Return maximum Double value on success
	 * @throws LdtpExecutionError on failure
	 */
	public double getMaxValue(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getDouble("getmaxvalue", params);
	}
	/**
	 * getMax Get maximum spin button value
	 *
	 * @param objName Object name inside the current window
	 * @return Return maximum Double value on success
	 * @throws LdtpExecutionError on failure
	 */
	public double getMax(String objName) throws LdtpExecutionError {
		return getMaxValue(objName);
	}
	/**
	 * getMinIncrement Get minimum increment value
	 *
	 * @param objName Object name inside the current window
	 * @return Return minimum increment Double value on success
	 * @throws LdtpExecutionError on failure
	 */
	public double getMinIncrement(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getDouble("getminincrement", params);
	}
	/**
	 * getMaxIncrement Get maximum increment value
	 *
	 * @param objName Object name inside the current window
	 * @return Return maximum increment Double value on success
	 * @throws LdtpExecutionError on failure
	 */
	public double getMaxIncrement(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return getDouble("getmaxincrement", params);
	}
	/**
	 * verifySliderVertical Verify slider is vertical
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifySliderVertical(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifyslidervertical", params);
	}
	/**
	 * verifySliderHorizontal Verify slider is horizontal
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifySliderHorizontal(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifysliderhorizontal", params);
	}
	/**
	 * verifyScrollbar Verify scrollbar exist or not
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyScrollbar(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifyscrollbar", params);
	}
	/**
	 * verifyScrollbarVertical Verify scrollbar is vertical
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyScrollbarVertical(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifyscrollbarvertical", params);
	}
	/**
	 * verifyScrollbarHorizontal Verify scrollbar is horizontal
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success, 0 on failure
	 */
	public int verifyScrollbarHorizontal(String objName) {
		Object[] params = new Object[]{windowName, objName};
		return verifyAction("verifyscrollbarhorizontal", params);
	}
	/**
	 * scrollUp Scroll up once
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int scrollUp(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("scrollup", params);
	}
	/**
	 * scrollDown Scroll down once
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int scrollDown(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("scrolldown", params);
	}
	/**
	 * scrollRight Scroll right once
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int scrollRight(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("scrollright", params);
	}
	/**
	 * scrollLeft Scroll left once
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int scrollLeft(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("scrollleft", params);
	}
	/**
	 * setMax Set maximum value in spin button
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int setMax(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("setmax", params);
	}
	/**
	 * setMin Set minimum value in spin button
	 *
	 * @param objName Object name inside the current window
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int setMin(String objName) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName};
		return doAction("setmin", params);
	}
	/**
	 * increase Increase slider value with given iterations
	 *
	 * @param objName Object name inside the current window
	 * @param iterations Repeat the action number of times
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int increase(String objName, int iterations) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, iterations};
		return doAction("increase", params);
	}
	/**
	 * decrease Decrease slider value with given iterations
	 *
	 * @param objName Object name inside the current window
	 * @param iterations Repeat the action number of times
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int decrease(String objName, int iterations) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, iterations};
		return doAction("decrease", params);
	}
	/**
	 * oneUp Up scrollbar with given iterations
	 *
	 * @param objName Object name inside the current window
	 * @param iterations Repeat the action number of times
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int oneUp(String objName, int iterations) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, iterations};
		return doAction("oneup", params);
	}
	/**
	 * oneDown Down scrollbar with given iterations
	 *
	 * @param objName Object name inside the current window
	 * @param iterations Repeat the action number of times
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int oneDown(String objName, int iterations) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, iterations};
		return doAction("onedown", params);
	}
	/**
	 * oneRight Right scrollbar with given iterations
	 *
	 * @param objName Object name inside the current window
	 * @param iterations Repeat the action number of times
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int oneRight(String objName, int iterations) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, iterations};
		return doAction("oneright", params);
	}
	/**
	 * oneLeft Left scrollbar with given iterations
	 *
	 * @param objName Object name inside the current window
	 * @param iterations Repeat the action number of times
	 * @return Return 1 on success
	 * @throws LdtpExecutionError on failure
	 */
	public int oneLeft(String objName, int iterations) throws LdtpExecutionError {
		Object[] params = new Object[]{windowName, objName, iterations};
		return doAction("oneleft", params);
	}
	// Image
	/**
	 * imageCapture Capture screenshot
	 *
	 * @param y Y co-ordinate from where to start capturing image
	 * @param width Width co-ordinate to end capturing image
	 * @param height Height co-ordinate to end capturing image
	 * @return Return filename where the captured image is stored on success
	 * @throws LdtpExecutionError on failure
	 */
	public String imageCapture(int y, int width, int height) throws LdtpExecutionError {
		return imageCapture("", 0, y, width, height);
	}
	/**
	 * imageCapture Capture screenshot
	 *
	 * @param width Width co-ordinate to end capturing image
	 * @param height Height co-ordinate to end capturing image
	 * @return Return filename where the captured image is stored on success
	 * @throws LdtpExecutionError on failure
	 */
	public String imageCapture(int width, int height) throws LdtpExecutionError {
		return imageCapture("", 0, 0, width, height);
	}
	/**
	 * imageCapture Capture screenshot
	 *
	 * @param height Height co-ordinate to end capturing image
	 * @return Return filename where the captured image is stored on success
	 * @throws LdtpExecutionError on failure
	 */
	public String imageCapture(int height) throws LdtpExecutionError {
		return imageCapture("", 0, 0, 0, height);
	}
	/**
	 * imageCapture Capture screenshot
	 *
	 * @return Return filename where the captured image is stored on success
	 * @throws LdtpExecutionError on failure
	 */
	public String imageCapture() throws LdtpExecutionError {
		return imageCapture("", 0, 0, 0, 0);
	}
	/**
	 * imageCapture Capture screenshot
	 *
	 * @param x X co-ordinate from where to start capturing image
	 * @param y Y co-ordinate from where to start capturing image
	 * @param width Width co-ordinate to end capturing image
	 * @param height Height co-ordinate to end capturing image
	 * @return Return filename where the captured image is stored on success
	 * @throws LdtpExecutionError on failure
	 */
	public String imageCapture(int x, int y, int width, int height) throws LdtpExecutionError {
		return imageCapture("", x, y, width, height);
	}
	/**
	 * imageCapture Capture screenshot
	 *
	 * @param windowName Capture only the window name rather than the complete desktop
	 * @return Return filename where the captured image is stored on success
	 * @throws LdtpExecutionError on failure
	 */
	public String imageCapture(String windowName) throws LdtpExecutionError {
		return imageCapture(windowName, 0, 0, 0, 0);
	}
	/**
	 * imageCapture Capture screenshot
	 *
	 * @param windowName Capture only the window name rather than the complete desktop
	 * @param x X co-ordinate from where to start capturing image
	 * @param y Y co-ordinate from where to start capturing image
	 * @param width Width co-ordinate to end capturing image
	 * @param height Height co-ordinate to end capturing image
	 * @return Return filename where the captured image is stored on success
	 * @throws LdtpExecutionError on failure
	 */
	public String imageCapture(String windowName, int x, int y, int width, int height) throws LdtpExecutionError {
		String data;
		Object[] params = new Object[]{windowName, x, y, width, height};
		String filename = null;
		try {
			java.io.File f = java.io.File.createTempFile("ldtp_", ".png");
			filename = f.getAbsolutePath();
			f.delete();
			data = getString("imagecapture", params);
			FileOutputStream fp = new FileOutputStream(filename);
			fp.write(Base64.decodeBase64(data));
			fp.close();
		} catch (java.io.FileNotFoundException ex) {
			throw new LdtpExecutionError(ex.getMessage());
		} catch (java.io.IOException ex) {
			throw new LdtpExecutionError(ex.getMessage());
		}
		return filename;
	}
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
		//Ldtp ldtp = new Ldtp("*Notepad");
		//System.out.println(ldtp.getTextValue("txt0"));
	}
}
