using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

using Ldtp;

namespace TestLdtpClient
{
    class Example1
    {

        public static void Test()
        {

            Ldtp.Ldtp l = new Ldtp.Ldtp("*Notepad*");
            l.WaitTillGuiExist();
            l.SelectMenuItem("mnuFile;mnuNew");

        }

    }
}
