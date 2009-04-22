from twisted.web import xmlrpc, server
from pyatspi import findDescendant, Registry
import subprocess
from time import sleep
from utils import ldtpize_accessible, \
    match_name_to_acc, list_guis, appmap_pairs
from waiters import ObjectExistsWaiter, GuiExistsWaiter, GuiNotExistsWaiter

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

    def xmlrpc_waittillguinotexist(self, window_name, timeout):
        waiter = GuiNotExistsWaiter(window_name, timeout)

        return int(waiter.run())

    def _click_object(self, obj):
        try:
            iaction = obj.queryAction()
        except NotImplementedError:
            pass
        else:
            for i in xrange(iaction.nActions):
                if iaction.getName(i) == 'click':
                    iaction.doAction(i)
                    return True
        return False

    def _get_object(self, window_name, obj_name):
        for gui in list_guis(self._desktop):
            if match_name_to_acc(window_name, gui):
                for name, obj in appmap_pairs(gui):
                    if name == obj_name:
                        return obj
        return None

    def xmlrpc_selectmenuitem(self, window_name, heirarchy):
        obj = self._get_object(window_name, heirarchy)

        if obj:
            return int(self._click_object(obj))

        return 0
    

