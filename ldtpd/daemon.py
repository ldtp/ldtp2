from twisted.web import xmlrpc, server
from pyatspi import findDescendant, Registry
import subprocess
from time import sleep
from utils import ldtpize_accessible, match_name_to_acc, list_guis
from waiters import ObjectExistsWaiter, GuiExistsWaiter

# waittillguiexist
# waittillguinotexist
# context (?)
# guiexist
# getobjectproperty
# click
# selectmenuitem
# settextvalue
# enterstring

class Ldtpd(xmlrpc.XMLRPC):
    def __init__(self):
        xmlrpc.XMLRPC.__init__(self)
        self._process = None
        self._desktop = Registry.getDesktop(0)

    def xmlrpc_isalive(self):
        return True

    def xmlrpc_launchapp(self, cmdline):
        try:
            self._process = subprocess.Popen(cmdline.split(' '))
        except Exception, e:
            raise xmlrpc.Fault(123, str(e))
        return self._process.pid

    def xmlrpc_guiexist(self, window_name, object_name):
        if object_name:
            waiter = ObjectExistsWaiter(window_name, object_name, 0)
        else:
            waiter = GuiExistsWaiter(window_name, 0)

        return int(waiter.run())

    def xmlrpc_waittillguiexist(self, window_name, object_name, timeout):
        if object_name:
            waiter = ObjectExistsWaiter(window_name, object_name, timeout)
        else:
            waiter = GuiExistsWaiter(window_name, timeout)

        return int(waiter.run())

    def xmlrpc_waittillguinotexist(self, window_name):
        return 1

    def xmlrpc_selectmenuitem(self, window_name):
        return 1
    

