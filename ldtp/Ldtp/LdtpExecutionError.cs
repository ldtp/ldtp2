using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Ldtp
{
    [Serializable]
    class LdtpExecutionError : Exception
    {
        public LdtpExecutionError(string message) : base(message)
        {
        }
    }
}
