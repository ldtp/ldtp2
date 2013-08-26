/*
 * WinLDTP 1.0
 * 
 * Author: Nagappan Alagappan <nalagappan@vmware.com>
 * Author: John Yingjun Li <yjli@vmware.com>
 * Copyright: Copyright (c) 2011-12 VMware, Inc. All Rights Reserved.
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
using CookComputing.XmlRpc;

using Ldtp;

namespace TestLdtpClient
{
    class Program
    {
        static void Main(string[] args)
        {

            Ldtp.Ldtp ldtp = new Ldtp.Ldtp("*gedit");
            /*
            int i;
            string[] cmdArgs = { };
            int ret = ldtp.LaunchApp("notepad", cmdArgs);
            Console.WriteLine("state #45 is {0}", ret);
            String[] windowList = ldtp.GetWindowList();
            for (i = 0; i < windowList.Length; i++)
                Console.WriteLine(windowList[i]);
            String[] appList = ldtp.GetAppList();
            for (i = 0; i < appList.Length; i++)
                Console.WriteLine(appList[i]);
            String[] objList = ldtp.GetObjectList();
            for (i = 0; i < objList.Length; i++)
                Console.WriteLine(objList[i] + " ");
            /**/
            Console.WriteLine("gedit: " + ldtp.GuiExist());
            Console.WriteLine("gedit: " + ldtp.GuiExist("Cancel"));
        }
    }
}
