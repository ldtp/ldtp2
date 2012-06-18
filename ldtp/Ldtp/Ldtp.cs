using System;
using System.Threading;
using System.Diagnostics;
using CookComputing.XmlRpc;
using System.Collections.Generic;

namespace Ldtp
{
    public interface ILdtp : IXmlRpcProxy
    {
        [XmlRpcMethod("launchapp")]
        int LaunchApp(string cmd, string[] args, int delay = 5,
                int env = 1, string lang = "");
        [XmlRpcMethod("getapplist")]
        string[] GetAppList();
        [XmlRpcMethod("getwindowlist")]
        String[] GetWindowList();
        [XmlRpcMethod("getobjectlist")]
        String[] GetObjectList(String windowName);
        [XmlRpcMethod("guiexist")]
        int GuiExist(String windowName, String objName = "");
        [XmlRpcMethod("isalive")]
        bool IsAlive();
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
    }
}
