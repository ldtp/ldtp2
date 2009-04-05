from twisted.web import xmlrpc, server
from pyatspi import findDescendant, Registry
import subprocess
from time import sleep
from utils import ldtpize_accessible, match_name_to_acc

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
        for gui in self._list_guis():
            if match_name_to_acc(window_name, gui):
                if object_name is None:
                    return 1
                else:
                    found = findDescendant(
                        gui,
                        lambda x: match_name_to_acc(object_name, x))
                    if found:
                        return 1
        return 0

    def xmlrpc_waittillguiexist(self, window_name, component, ):
        return 1

    def xmlrpc_waittillguinotexist(self, window_name):
        return 1

    def xmlrpc_selectmenuitem(self, window_name):
        return 1
    
    def _list_guis(self):
        guis = []
        for app in self._desktop:
            if not app: continue
            for gui in app:
                if not gui: continue
                guis.append(gui)
        return guis

