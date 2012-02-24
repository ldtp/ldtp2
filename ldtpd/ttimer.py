#! /usr/bin/env python
""" 
ttimer: Thread callback timer, it execute your callback function periodically. 

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Author   : H.K.Ong
Date     : 27-03-2008
Website  : http://linux.byexamples.com
Revision : 1
"""
import sys,thread,time

class ttimer():
    """Threading callback timer - threading timer will callback your function periodically.
interval - interval callback periodically, in sec
retry    - execute how many times? -1 is infinity
cbfunc   - callback function
cbparam  - parameter in list

i.e t=ttimer(1,10,myfunc,["myparam"])"""

    def __init__(self, interval, retry, cbfunc, cbparam=[]):
        self.is_start=False
        self.is_end=False

        # doing my thread stuff now.
        thread.start_new_thread(self._callback,(interval,retry,cbfunc,cbparam,))

    def Start(self):
        "start the thread"
        self.mytime=time.time()
        self.is_start=True
	self.is_end=False

    def Stop(self):
        "stop the thread."
        self.mytime=time.time()
        self.is_start=False
        self.is_end=True

    def IsStop(self):
        "Is the thread already end? return True if yes."
        if self.is_end:
            return True
        else:
            return False

    def _callback(self,interval,retry,cbfunc,cbparam=[]):
        """ This is the private thread loop, call start() to start the threading timer."""
        self.retry=retry
        retry=0

        if self.is_end:
            return None

        while True:
            if self.is_end:
                break
            if self.retry==-1:
                pass
            elif retry>=self.retry:
                break

            if self.is_start:
                #check time
                tmptime=time.time()
                if tmptime >=(self.mytime + interval):
                    cbfunc(cbparam) # callback your function
                    self.mytime=time.time()
                    retry+=1
                else:
                    pass
            # Modified interval from orignal code
            # by Nagappan Alagappan <nagappan@gmail.com>
            # as 0.001 second is quick for accessibility scan
            time.sleep(interval)

        self.is_end=True

def dummy_cbf(param=[]):
    "sample dummy callback function"
    print "hello %-12s %s" % (param[0], time.strftime("%H:%M:%S"))

def main(argv=None):
    "sample main()"
    # interval, retry, cbfunction
    print "type 'quit' to end"

    timer  =ttimer (0.5, 5, dummy_cbf, ["linux"])
    timer2 =ttimer (0.6, 5, dummy_cbf, ["by"])
    timer3 =ttimer (0.7, 5, dummy_cbf, ["examples"])
    timer4 =ttimer (  1,-1, dummy_cbf, ["python"])
    timer.Start()
    timer2.Start()
    timer3.Start()
    timer4.Start()

    # main program need to stop the thread manually.
    while 1:
        time.sleep(0.001)
        cmd=raw_input()
        if cmd=="quit":
            timer.Stop()
            timer2.Stop()
            timer3.Stop()
            timer4.Stop()
            if timer.IsStop() and timer2.IsStop() and timer3.IsStop() and timer4.IsStop():
                sys.exit(0)
        else:
            print "type 'quit' to end"

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        pass
