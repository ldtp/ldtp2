/*
 * Cobra WinLDTP 3.5
 * 
 * Author: Nagappan Alagappan <nalagappan@vmware.com>
 * Author: John Yingjun Li <yjli@vmware.com>
 * Copyright: Copyright (c) 2011-13 VMware, Inc. All Rights Reserved.
 * License: MIT license
 * 
 * http://ldtp.freedesktop.org
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to do
 * so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
*/
using System;
using System.IO;
using System.Threading;
using System.Diagnostics;
using CookComputing.XmlRpc;
using System.Collections.Generic;

namespace Ldtp
{
    public interface ILdtp : IXmlRpcProxy
    {
        [XmlRpcMethod("isalive")]
        bool IsAlive();
        [XmlRpcMethod("launchapp")]
        int LaunchApp(string cmd, string[] args, int delay = 5,
            int env = 1, string lang = "");
        [XmlRpcMethod("appundertest")]
        int AppUnderTest(String appUnderTest);
        [XmlRpcMethod("getapplist")]
        string[] GetAppList();
        [XmlRpcMethod("getwindowlist")]
        String[] GetWindowList();
        [XmlRpcMethod("getobjectlist")]
        String[] GetObjectList(String windowName);
        [XmlRpcMethod("getobjectinfo")]
        String[] GetObjectInfo(String windowName, String objName);
        [XmlRpcMethod("getobjectproperty")]
        String GetObjectProperty(String windowName, String objName,
            String property);
        [XmlRpcMethod("getaccesskey")]
        String GetAccessKey(String windowName, String objName);
        [XmlRpcMethod("getchild")]
        String[] GetChild(String windowName, String childName,
            String role = "", String property = "");
        [XmlRpcMethod("getobjectsize")]
        int[] GetObjectSize(String windowName, String objName);
        [XmlRpcMethod("getwindowsize")]
        int[] GetWindowSize(String windowName);
        [XmlRpcMethod("handletablecell")]
        int HandleTableCell();
        [XmlRpcMethod("unhandletablecell")]
        int UnHandleTableCell();
        [XmlRpcMethod("remap")]
        int ReMap(String windowName);
        [XmlRpcMethod("wait")]
        int WaitTime(int timeout = 5);
        [XmlRpcMethod("getobjectnameatcoords")]
        String[] GetObjectNameAtCoords(int waitTime = 0);
        [XmlRpcMethod("guiexist")]
        int GuiExist(String windowName, String objName = "");
        [XmlRpcMethod("objectexist")]
        int ObjectExist(String windowName, String objName);
        [XmlRpcMethod("waittillguiexist")]
        int WaitTillGuiExist(String windowName, String objName = "",
            int guiTimeOut = 30, String state = "");
        [XmlRpcMethod("waittillguinotexist")]
        int WaitTillGuiNotExist(String windowName, String objName = "",
            int guiTimeOut = 30, String state = "");
        [XmlRpcMethod("poll_events")]
        string PollEvents();
        [XmlRpcMethod("getlastlog")]
        string GetLastLog();
        [XmlRpcMethod("startprocessmonitor")]
        int StartProcessMonitor(string processName, int interval = 2);
        [XmlRpcMethod("stopprocessmonitor")]
        int StopProcessMonitor(string processName);
        [XmlRpcMethod("getcpustat")]
        double[] GetCpuStat(string processName);
        [XmlRpcMethod("getmemorystat")]
        long[] GetMemoryStat(string processName);
        [XmlRpcMethod("onwindowcreate")]
        int OnWindowCreate(string windowName);
        [XmlRpcMethod("removecallback")]
        int RemoveCallback(string windowName);
        [XmlRpcMethod("maximizewindow")]
        int MaximizeWindow(String windowName);
        [XmlRpcMethod("minimizewindow")]
        int MinimizeWindow(String windowName);
        [XmlRpcMethod("closewindow")]
        int CloseWindow(String windowName);
        [XmlRpcMethod("getallstates")]
        string[] GetAllStates(String windowName, String objName);
        [XmlRpcMethod("hasstate")]
        int HasState(String windowName, String objName,
            String state, int guiTimeOut = 0);
        [XmlRpcMethod("grabfocus")]
        int GrabFocus(String windowName, String objName = "");
        [XmlRpcMethod("click")]
        int Click(String windowName, String objName);
        [XmlRpcMethod("check")]
        int Check(String windowName, String objName);
        [XmlRpcMethod("uncheck")]
        int UnCheck(String windowName, String objName);
        [XmlRpcMethod("verifycheck")]
        int VerifyCheck(String windowName, String objName);
        [XmlRpcMethod("verifyuncheck")]
        int VerifyUnCheck(String windowName, String objName);
        [XmlRpcMethod("stateenabled")]
        int StateEnabled(String windowName, String objName);
        [XmlRpcMethod("objtimeout ")]
        int ObjectTimeOut(int objectTimeOut);
        [XmlRpcMethod("guitimeout ")]
        int GuiTimeOut(int guiTimeOut);
        [XmlRpcMethod("selectmenuitem")]
        int SelectMenuItem(String windowName, String objName);
        [XmlRpcMethod("doesmenuitemexist")]
        int DoesSelectMenuItemExist(String windowName, String objName);
        [XmlRpcMethod("listsubmenus")]
        String[] ListSubMenus(String windowName, String objName);
        [XmlRpcMethod("menucheck")]
        int MenuCheck(String windowName, String objName);
        [XmlRpcMethod("menuuncheck")]
        int MenuUnCheck(String windowName, String objName);
        [XmlRpcMethod("menuitemenabled")]
        int MenuItemEnabled(String windowName, String objName);
        [XmlRpcMethod("verifymenucheck")]
        int VerifyMenuCheck(String windowName, String objName);
        [XmlRpcMethod("verifymenuuncheck")]
        int VerifyMenuUnCheck(String windowName, String objName);
        [XmlRpcMethod("generatekeyevent")]
        int GenerateKeyEvent(string data);
        [XmlRpcMethod("keypress")]
        int KeyPress(string data);
        [XmlRpcMethod("keyrelease")]
        int KeyRelease(string data);
        [XmlRpcMethod("enterstring")]
        int EnterString(string windowName, string objName = "", string data = "");
        [XmlRpcMethod("settextvalue")]
        int SetTextValue(String windowName, String objName, String value);
        [XmlRpcMethod("gettextvalue")]
        String GetTextValue(String windowName, String objName,
            int startPos = 0, int endPos = 0);
        [XmlRpcMethod("verifypartialmatch")]
        int VerifyPartialText(String windowName, String objName, string value);
        [XmlRpcMethod("verifysettext")]
        int VerifySetText(String windowName, String objName, string value);
        [XmlRpcMethod("activatetext")]
        int ActivateText(String windowName, String objName);
        [XmlRpcMethod("appendtext")]
        int AppendText(String windowName, String objName, string value);
        [XmlRpcMethod("inserttext")]
        int InsertText(String windowName, String objName, int postion, string value);
        [XmlRpcMethod("istextstateenabled")]
        int IsTextStateEnabled(String windowName, String objName);
        [XmlRpcMethod("getcharcount")]
        int GetCharCount(String windowName, String objName);
        [XmlRpcMethod("copytext")]
        int CopyText(String windowName, String objName, int start, int end = -1);
        [XmlRpcMethod("cuttext")]
        int CutText(String windowName, String objName, int start, int end = -1);
        [XmlRpcMethod("deletetext")]
        int DeleteText(String windowName, String objName, int start, int end = -1);
        [XmlRpcMethod("pastetext")]
        int PasteText(String windowName, String objName, int postion);
        [XmlRpcMethod("selectitem")]
        int SelectItem(String windowName, String objName, String item);
        [XmlRpcMethod("comboselect")]
        int ComboSelect(String windowName, String objName, String item);
        [XmlRpcMethod("verifyselect")]
        int VerifyComboSelect(String windowName, String objName, String item);
        [XmlRpcMethod("selectindex")]
        int SelectIndex(String windowName, String objName, int index);
        [XmlRpcMethod("getcombovalue")]
        String GetComboValue(String windowName, String objName);
        [XmlRpcMethod("showlist")]
        int ShowList(String windowName, String objName);
        [XmlRpcMethod("hidelist")]
        int HideList(String windowName, String objName);
        [XmlRpcMethod("verifydropdown")]
        int VerifyDropDown(String windowName, String objName);
        [XmlRpcMethod("verifyshowlist")]
        int VerifyShowList(String windowName, String objName);
        [XmlRpcMethod("verifyhidelist")]
        int VerifyHideList(String windowName, String objName);
        [XmlRpcMethod("getallitem")]
        string[] GetAllItem(String windowName, String objName);
        [XmlRpcMethod("generatemouseevent")]
        int GenerateMouseEvent(int x, int y, String type = "b1p");
        [XmlRpcMethod("mouseleftclick")]
        int MouseLeftClick(String windowName, String objName);
        [XmlRpcMethod("mouserightclick")]
        int MouseRightClick(String windowName, String objName);
        [XmlRpcMethod("doubleclick")]
        int DoubleClick(String windowName, String objName);
        [XmlRpcMethod("doubleclickrow")]
        int DoubleClickRow(String windowName, String objName, String text);
        [XmlRpcMethod("rightclick")]
        int RightClick(String windowName, String objName, String text);
        [XmlRpcMethod("simulatemousemove")]
        int SimulateMouseMove(int source_x, int source_y, int dest_x,
            int dest_y, double delay = 0.0);
        [XmlRpcMethod("selecttab")]
        int SelectTab(String windowName, String objName, String tabName);
        [XmlRpcMethod("selecttabindex")]
        int SelectTabIndex(String windowName, String objName, int index);
        [XmlRpcMethod("gettabname")]
        String GetTabName(String windowName, String objName, int index);
        [XmlRpcMethod("gettabcount")]
        int GetTabCount(String windowName, String objName);
        [XmlRpcMethod("verifytabname")]
        int VerifyTabName(String windowName, String objName, String tabName);
        [XmlRpcMethod("getrowcount")]
        int GetRowCount(String windowName, String objName);
        [XmlRpcMethod("selectrow")]
        int SelectRow(String windowName, String objName, String text,
            bool partialMatch = false);
        [XmlRpcMethod("verifyselectrow")]
        int VerifySelectRow(String windowName, String objName, String text,
            bool partialMatch = false);
        [XmlRpcMethod("selectrowpartialmatch")]
        int SelectRowPartialMatch(String windowName, String objName, String text);
        [XmlRpcMethod("selectrowindex")]
        int SelectRowIndex(String windowName, String objName, int index);
        [XmlRpcMethod("getcellvalue")]
        String GetCellValue(String windowName, String objName, int row,
            int column = 0);
        [XmlRpcMethod("setcellvalue")]
        String SetCellValue(String windowName, String objName, int row,
            int column = 0, String data = null);
        [XmlRpcMethod("getcellsize")]
        String GetCellSize(String windowName, String objName, int row,
            int column = 0);
        [XmlRpcMethod("expandtablecell")]
        int ExpandTableCell(String windowName, String objName, int index);
        [XmlRpcMethod("gettablerowindex")]
        int GetTableRowIndex(String windowName, String objName, String cellValue);
        [XmlRpcMethod("doesrowexist")]
        int DoesRowExist(String windowName, String objName, String text,
            bool partialMatch = false);
        [XmlRpcMethod("getvalue")]
        double GetValue(String windowName, String objName);
        [XmlRpcMethod("getslidervalue")]
        double GetSliderValue(String windowName, String objName);
        [XmlRpcMethod("setvalue")]
        int SetValue(String windowName, String objName, double value);
        [XmlRpcMethod("verifysetvalue")]
        int VerifySetValue(String windowName, String objName, double value);
        [XmlRpcMethod("getminvalue")]
        double GetMinValue(String windowName, String objName);
        [XmlRpcMethod("getmaxvalue")]
        double GetMaxValue(String windowName, String objName);
        [XmlRpcMethod("getmin")]
        double GetMin(String windowName, String objName);
        [XmlRpcMethod("getmax")]
        double GetMax(String windowName, String objName);
        [XmlRpcMethod("getminincrement")]
        double GetMinIncrement(String windowName, String objName);
        [XmlRpcMethod("verifyslidervertical")]
        int VerifySliderVertical(String windowName, String objName);
        [XmlRpcMethod("verifysliderhorizontal")]
        int VerifySliderHorizontal(String windowName, String objName);
        [XmlRpcMethod("setmin")]
        int SetMin(String windowName, String objName);
        [XmlRpcMethod("setmax")]
        int SetMax(String windowName, String objName);
        [XmlRpcMethod("increase")]
        int Increase(String windowName, String objName, int iterations);
        [XmlRpcMethod("decrease")]
        int Decrease(String windowName, String objName, int iterations);
        [XmlRpcMethod("imagecapture")]
        string ImageCapture(string windowName = "", int x = 0, int y = 0,
            int width = -1, int height = -1);
        [XmlRpcMethod("onedown")]
        int OneDown(String windowName, String objName, int iterations);
        [XmlRpcMethod("one")]
        int OneUp(String windowName, String objName, int iterations);
        [XmlRpcMethod("oneright")]
        int OneRight(String windowName, String objName, int iterations);
        [XmlRpcMethod("oneleft")]
        int OneLeft(String windowName, String objName, int iterations);
        [XmlRpcMethod("scrolldown")]
        int ScrollDown(String windowName, String objName);
        [XmlRpcMethod("scrollup")]
        int ScrollUp(String windowName, String objName);
        [XmlRpcMethod("scrollleft")]
        int ScrollLeft(String windowName, String objName);
        [XmlRpcMethod("scrollright")]
        int ScrollRight(String windowName, String objName);
        [XmlRpcMethod("verifyscrollbar")]
        int VerifyScrollBar(String windowName, String objName);
        [XmlRpcMethod("verifyscrollbarhorizontal")]
        int VerifyScrollBarHorizontal(String windowName, String objName);
        [XmlRpcMethod("verifyscrollbarvertical")]
        int VerifyScrollBarVertical(String windowName, String objName);
    }
    public class Ldtp
    {
        ILdtp proxy;
        Process ps = null;
        String windowName = null;
        String serverAddr = null;
        String serverPort = null;
        Boolean windowsEnv = false;
        private void connectToServer()
        {
            if (serverAddr == null)
                serverAddr = Environment.GetEnvironmentVariable("LDTP_SERVER_ADDR");
            if (serverAddr == null)
                serverAddr = "localhost";
            if (serverPort == null)
                serverPort = Environment.GetEnvironmentVariable("LDTP_SERVER_PORT");
            if (serverPort == null)
                serverPort = "4118";
            String tmpEnv = Environment.GetEnvironmentVariable("LDTP_WINDOWS");
            if (tmpEnv != null)
                windowsEnv = true;
            else
            {
                tmpEnv = Environment.GetEnvironmentVariable("LDTP_LINUX");
                if (tmpEnv != null)
                    windowsEnv = false;
                else
                {
                    windowsEnv = true;
                }
            }
            proxy = (ILdtp)XmlRpcProxyGen.Create(typeof(ILdtp));
            String url = String.Format("http://{0}:{1}/RPC2", serverAddr, serverPort);
            proxy.Url = url;
            IsAlive();
        }
        private Boolean IsAlive()
        {
            Boolean isAlive = false;
            try
            {
                isAlive = proxy.IsAlive();
            }
            catch
            {
                // Do nothing on exception
                ;
            }
            if (!isAlive)
                launchLdtpProcess();
            return isAlive;
        }
        void InternalLaunchProcess(object data)
        {
            Process ps = data as Process;
            // Wait for the application to quit
            ps.WaitForExit();
            // Close the handle, so that we won't leak memory
            ps.Close();
            ps = null;
        }
        private void launchLdtpProcess()
        {
            String cmd;
            if (windowsEnv)
                // Launch Windows LDTP
                cmd = "CobraWinLDTP.exe";
            else
                // Launch Linux LDTP
                cmd = "ldtp";
            ps = new Process();
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = cmd;
                psi.UseShellExecute = true;
                psi.WindowStyle = ProcessWindowStyle.Hidden;
                ps.StartInfo = psi;
                ps.Start();
                Thread thread = new Thread(new ParameterizedThreadStart(
                    InternalLaunchProcess));
                // Clean up in different thread
                //thread.Start(ps);
                // Wait 5 seconds after launching
                Thread.Sleep(5000);
            }
            catch (Exception ex)
            {
                throw new LdtpExecutionError(ex.Message);
            }
        }
        ~Ldtp()
        {
            Console.WriteLine("Destructor");
            if (ps != null)
            {
                try
                {
                    ps.Kill();
                }
                catch
                {
                    // Silently ignore any exception
                }
            }
        }
        public Ldtp(String windowName, String serverAddr = "localhost",
                String serverPort = "4118", bool windowsEnv = true)
        {
            if (windowName == null || windowName == "")
            {
                throw new LdtpExecutionError("Window name missing");
            }
            this.serverAddr = serverAddr;
            this.serverPort = serverPort;
            this.windowName = windowName;
            this.windowsEnv = windowsEnv;
            connectToServer();
        }
        public int LaunchApp(string cmd, string[] args, int delay = 5,
                int env = 1, string lang = "")
        {
            try
            {
                return proxy.LaunchApp(cmd, args, delay, env, lang);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int AppUnderTest(String appUnderTest)
        {
            try
            {
                return proxy.AppUnderTest(appUnderTest);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String[] GetAppList()
        {
            try
            {
                return proxy.GetAppList();
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String[] GetWindowList()
        {
            try
            {
                return proxy.GetWindowList();
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String[] GetObjectList()
        {
            try
            {
                return proxy.GetObjectList(windowName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int GuiExist(String objName = "")
        {
            try
            {
                return proxy.GuiExist(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ObjectExist(String objName)
        {
            try
            {
                return proxy.ObjectExist(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String[] GetObjectInfo(String objName)
        {
            try
            {
                return proxy.GetObjectInfo(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String GetAccessKey(String objName)
        {
            try
            {
                return proxy.GetAccessKey(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String GetObjectProperty(String objName, String property)
        {
            try
            {
                return proxy.GetObjectProperty(windowName, objName, property);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String[] GetChild(String childName, String role = "", String property = "")
        {
            try
            {
                return proxy.GetChild(windowName, childName, role, property);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int[] GetObjectSize(String objName)
        {
            try
            {
                return proxy.GetObjectSize(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int[] GetWindowSize()
        {
            try
            {
                return proxy.GetWindowSize(windowName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int HandleTableCell()
        {
            try
            {
                return proxy.HandleTableCell();
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int UnHandleTableCell()
        {
            try
            {
                return proxy.UnHandleTableCell();
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ReMap()
        {
            try
            {
                return proxy.ReMap(windowName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int WaitTime(int timeout = 5)
        {
            try
            {
                return proxy.WaitTime(timeout);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String[] GetObjectNameAtCoords(int waitTime = 0)
        {
            try
            {
                return proxy.GetObjectNameAtCoords(waitTime);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int WaitTillGuiExist(String objName = "", int guiTimeOut = 30, String state = "")
        {
            try
            {
                return proxy.WaitTillGuiExist(windowName, objName, guiTimeOut, state);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int WaitTillGuiNotExist(String objName = "", int guiTimeOut = 30, String state = "")
        {
            try
            {
                return proxy.WaitTillGuiNotExist(windowName, objName, guiTimeOut, state);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public string PollEvents()
        {
            try
            {
                return proxy.PollEvents();
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public string GetLastLog()
        {
            try
            {
                return proxy.GetLastLog();
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int StartProcessMonitor(string processName, int interval = 2)
        {
            try
            {
                return proxy.StartProcessMonitor(processName, interval);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int StopProcessMonitor(string processName)
        {
            try
            {
                return proxy.StopProcessMonitor(processName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public double[] GetCpuStat(string processName)
        {
            try
            {
                return proxy.GetCpuStat(processName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public long[] GetMemoryStat(string processName)
        {
            try
            {
                return proxy.GetMemoryStat(processName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        // FIXME: Callback function handle should be taken as argument and
        // that should be called when the window appears
        public int OnWindowCreate()
        {
            try
            {
                return proxy.OnWindowCreate(windowName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int RemoveCallback()
        {
            try
            {
                return proxy.RemoveCallback(windowName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int MaximizeWindow()
        {
            try
            {
                return proxy.MaximizeWindow(windowName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int MinimizeWindow()
        {
            try
            {
                return proxy.MinimizeWindow(windowName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int CloseWindow()
        {
            try
            {
                return proxy.CloseWindow(windowName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public string[] GetAllStates(String objName)
        {
            try
            {
                return proxy.GetAllStates(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int HasState(String objName, String state, int guiTimeOut = 0)
        {
            try
            {
                return proxy.HasState(windowName, objName, state, guiTimeOut);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int GrabFocus(String objName = "")
        {
            try
            {
                return proxy.GrabFocus(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int Click(String objName)
        {
            try
            {
                return proxy.Click(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int Check(String objName)
        {
            try
            {
                return proxy.Check(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int UnCheck(String objName)
        {
            try
            {
                return proxy.UnCheck(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyCheck(String objName)
        {
            try
            {
                return proxy.VerifyCheck(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyUnCheck(String objName)
        {
            try
            {
                return proxy.VerifyUnCheck(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int StateEnabled(String objName)
        {
            try
            {
                return proxy.StateEnabled(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ObjectTimeOut(int objectTimeOut)
        {
            try
            {
                return proxy.ObjectTimeOut(objectTimeOut);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int GuiTimeOut(int guiTimeOut)
        {
            try
            {
                return proxy.GuiTimeOut(guiTimeOut);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SelectMenuItem(String objName)
        {
            try
            {
                return proxy.SelectMenuItem(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int DoesSelectMenuItemExist(String objName)
        {
            try
            {
                return proxy.DoesSelectMenuItemExist(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String[] ListSubMenus(String objName)
        {
            try
            {
                return proxy.ListSubMenus(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int MenuCheck(String objName)
        {
            try
            {
                return proxy.MenuCheck(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int MenuUnCheck(String objName)
        {
            try
            {
                return proxy.MenuUnCheck(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int MenuItemEnabled(String objName)
        {
            try
            {
                return proxy.MenuItemEnabled(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyMenuCheck(String objName)
        {
            try
            {
                return proxy.VerifyMenuCheck(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyMenuUnCheck(String objName)
        {
            try
            {
                return proxy.VerifyMenuUnCheck(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int GenerateKeyEvent(string data)
        {
            try
            {
                return proxy.GenerateKeyEvent(data);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int KeyPress(string data)
        {
            try
            {
                return proxy.KeyPress(data);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int KeyRelease(string data)
        {
            try
            {
                return proxy.KeyRelease(data);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int EnterString(string objName = "", string data = "")
        {
            try
            {
                return proxy.EnterString(windowName, objName, data);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SetTextValue(String objName, String value)
        {
            try
            {
                return proxy.SetTextValue(windowName, objName, value);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String GetTextValue(String objName, int startPos = 0, int endPos = 0)
        {
            try
            {
                return proxy.GetTextValue(windowName, objName, startPos, endPos);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyPartialText(String objName, string value)
        {
            try
            {
                return proxy.VerifyPartialText(windowName, objName, value);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifySetText(String objName, string value)
        {
            try
            {
                return proxy.VerifySetText(windowName, objName, value);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ActivateText(String objName)
        {
            try
            {
                return proxy.ActivateText(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int AppendText(String objName, string value)
        {
            try
            {
                return proxy.AppendText(windowName, objName, value);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int InsertText(String objName, int postion, string value)
        {
            try
            {
                return proxy.InsertText(windowName, objName, postion, value);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int IsTextStateEnabled(String objName)
        {
            return proxy.IsTextStateEnabled(windowName, objName);
        }
        public int GetCharCount(String objName)
        {
            try
            {
                return proxy.GetCharCount(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int CopyText(String objName, int start, int end = -1)
        {
            try
            {
                return proxy.CopyText(windowName, objName, start, end);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int CutText(String objName, int start, int end = -1)
        {
            try
            {
                return proxy.CutText(windowName, objName, start, end);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int DeleteText(String objName, int start, int end = -1)
        {
            try
            {
                return proxy.DeleteText(windowName, objName, start, end);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int PasteText(String objName, int postion)
        {
            try
            {
                return proxy.PasteText(windowName, objName, postion);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SelectItem(String objName, String item)
        {
            try
            {
                return proxy.SelectItem(windowName, objName, item);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ComboSelect(String objName, String item)
        {
            try
            {
                return proxy.ComboSelect(windowName, objName, item);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyComboSelect(String objName, String item)
        {
            try
            {
                return proxy.VerifyComboSelect(windowName, objName, item);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SelectIndex(String objName, int index)
        {
            try
            {
                return proxy.SelectIndex(windowName, objName, index);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String GetComboValue(String objName)
        {
            try
            {
                return proxy.GetComboValue(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ShowList(String objName)
        {
            try
            {
                return proxy.ShowList(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int HideList(String objName)
        {
            try
            {
                return proxy.HideList(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyDropDown(String objName)
        {
            try
            {
                return proxy.VerifyDropDown(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyShowList(String objName)
        {
            try
            {
                return proxy.VerifyShowList(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyHideList(String objName)
        {
            try
            {
                return proxy.VerifyHideList(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public string[] GetAllItem(String objName)
        {
            try
            {
                return proxy.GetAllItem(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int GenerateMouseEvent(int x, int y, String type = "b1p")
        {
            try
            {
                return proxy.GenerateMouseEvent(x, y, type);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int MouseLeftClick(String objName)
        {
            try
            {
                return proxy.MouseLeftClick(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int MouseRightClick(String objName)
        {
            try
            {
                return proxy.MouseRightClick(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int DoubleClick(String objName)
        {
            try
            {
                return proxy.DoubleClick(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int DoubleClickRow(String objName, String text)
        {
            try
            {
                return proxy.DoubleClickRow(windowName, objName, text);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int RightClick(String objName, String text)
        {
            try
            {
                return proxy.RightClick(windowName, objName, text);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SimulateMouseMove(int source_x, int source_y, int dest_x,
            int dest_y, double delay = 0.0)
        {
            try
            {
                return proxy.SimulateMouseMove(source_x, source_y, dest_x, dest_y, delay);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SelectTab(String objName, String tabName)
        {
            try
            {
                return proxy.SelectTab(windowName, objName, tabName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SelectTabIndex(String objName, int index)
        {
            try
            {
                return proxy.SelectTabIndex(windowName, objName, index);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String GetTabName(String objName, int index)
        {
            try
            {
                return proxy.GetTabName(windowName, objName, index);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int GetTabCount(String objName)
        {
            try
            {
                return proxy.GetTabCount(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyTabName(String objName, String tabName)
        {
            try
            {
                return proxy.VerifyTabName(windowName, objName, tabName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int GetRowCount(String objName)
        {
            try
            {
                return proxy.GetRowCount(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SelectRow(String objName, String text, bool partialMatch = false)
        {
            try
            {
                return proxy.SelectRow(windowName, objName, text, partialMatch);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifySelectRow(String objName, String text, bool partialMatch = false)
        {
            try
            {
                return proxy.VerifySelectRow(windowName, objName, text, partialMatch);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SelectRowPartialMatch(String objName, String text)
        {
            try
            {
                return proxy.SelectRowPartialMatch(windowName, objName, text);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SelectRowIndex(String objName, int index)
        {
            try
            {
                return proxy.SelectRowIndex(windowName, objName, index);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String GetCellValue(String objName, int row, int column = 0)
        {
            try
            {
                return proxy.GetCellValue(windowName, objName, row, column);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String SetCellValue(String objName, int row, int column = 0, String data = null)
        {
            try
            {
                return proxy.SetCellValue(windowName, objName, row, column, data);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public String GetCellSize(String objName, int row, int column = 0)
        {
            try
            {
                return proxy.GetCellSize(windowName, objName, row, column);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ExpandTableCell(String objName, int index)
        {
            try
            {
                return proxy.ExpandTableCell(windowName, objName, index);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int GetTableRowIndex(String objName, String cellValue)
        {
            try
            {
                return proxy.GetTableRowIndex(windowName, objName, cellValue);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int DoesRowExist(String objName, String text, bool partialMatch = false)
        {
            try
            {
                return proxy.DoesRowExist(windowName, objName, text, partialMatch);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public double GetValue(String objName)
        {
            try
            {
                return proxy.GetValue(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public double GetSliderValue(String objName)
        {
            try
            {
                return proxy.GetSliderValue(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SetValue(String objName, double value)
        {
            try
            {
                return proxy.SetValue(windowName, objName, value);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifySetValue(String objName, double value)
        {
            try
            {
                return proxy.VerifySetValue(windowName, objName, value);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public double GetMinValue(String objName)
        {
            try
            {
                return proxy.GetMinValue(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public double GetMaxValue(String objName)
        {
            try
            {
                return proxy.GetMaxValue(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public double GetMin(String objName)
        {
            try
            {
                return proxy.GetMin(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public double GetMax(String objName)
        {
            try
            {
                return proxy.GetMax(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public double GetMinIncrement(String objName)
        {
            try
            {
                return proxy.GetMinIncrement(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifySliderVertical(String objName)
        {
            try
            {
                return proxy.VerifySliderVertical(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifySliderHorizontal(String objName)
        {
            try
            {
                return proxy.VerifySliderHorizontal(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SetMin(String objName)
        {
            try
            {
                return proxy.SetMin(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int SetMax(String objName)
        {
            try
            {
                return proxy.SetMax(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int Increase(String objName, int iterations)
        {
            try
            {
                return proxy.Increase(windowName, objName, iterations);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int Decrease(String objName, int iterations)
        {
            try
            {
                return proxy.Decrease(windowName, objName, iterations);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public string ImageCapture(String windowName = null, String outFile = null,
            int x = 0, int y = 0, int width = -1, int height = -1)
        {
            try
            {
                string path;
                if (outFile == null)
                    path = Path.GetTempPath() + Path.GetRandomFileName() + ".png";
                else
                    path = outFile;
                string data = proxy.ImageCapture(windowName, x, y, width, height);
                using (FileStream fs = File.Open(path, FileMode.Open,
                    FileAccess.Write))
                {
                    Byte[] decodedText = Convert.FromBase64String(data);
                    fs.Write(decodedText, 0, decodedText.Length);
                    fs.Close();
                }
                return path;
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int OneDown(String objName, int iterations)
        {
            try
            {
                return proxy.OneDown(windowName, objName, iterations);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int OneUp(String objName, int iterations)
        {
            try
            {
                return proxy.OneUp(windowName, objName, iterations);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int OneRight(String objName, int iterations)
        {
            try
            {
                return proxy.OneRight(windowName, objName, iterations);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int OneLeft(String objName, int iterations)
        {
            try
            {
                return proxy.OneLeft(windowName, objName, iterations);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ScrollDown(String objName)
        {
            try
            {
                return proxy.ScrollDown(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ScrollLeft(String objName)
        {
            try
            {
                return proxy.ScrollLeft(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ScrollUp(String objName)
        {
            try
            {
                return proxy.ScrollUp(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int ScrollRight(String objName)
        {
            try
            {
                return proxy.ScrollRight(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyScrollBar(String objName)
        {
            try
            {
                return proxy.VerifyScrollBar(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyScrollBarVertical(String objName)
        {
            try
            {
                return proxy.VerifyScrollBarVertical(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
        public int VerifyScrollBarHorizontal(String objName)
        {
            try
            {
                return proxy.VerifyScrollBarHorizontal(windowName, objName);
            }
            catch (XmlRpcFaultException ex)
            {
                throw new LdtpExecutionError(ex.FaultString);
            }
        }
    }
}
