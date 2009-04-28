from twisted.web import xmlrpc, server
from pyatspi import findDescendant, Registry
import subprocess
from time import sleep
from utils import ldtpize_accessible, \
    match_name_to_acc, list_guis, appmap_pairs
from waiters import ObjectExistsWaiter, GuiExistsWaiter, GuiNotExistsWaiter
from server_exception import LdtpServerException
import os

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
        os.environ['NO_GAIL'] = '0'
        os.environ['NO_AT_BRIDGE'] = '0'
        try:
            self._process = subprocess.Popen(cmdline.split(' '))
        except Exception, e:
            raise LdtpServerException(str(e))
        os.environ['NO_GAIL'] = '1'
        os.environ['NO_AT_BRIDGE'] = '1'
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
            raise LdtpServerException(
                'Object does not have an Action interface')
        else:
            for i in xrange(iaction.nActions):
                if iaction.getName(i) == 'click':
                    iaction.doAction(i)
                    return
            raise LdtpServerException('Object does not have a "click" action')
        

    def _get_object(self, window_name, obj_name):
        for gui in list_guis(self._desktop):
            if match_name_to_acc(window_name, gui):
                for name, obj in appmap_pairs(gui):
                    if name == obj_name:
                        return obj
        raise LdtpServerException(
            'Unable to find object name in application map')

    def xmlrpc_selectmenuitem(self, window_name, heirarchy):
        obj = self._get_object(window_name, heirarchy)

        self._click_object(obj)

        return 1

    def xmlrpc_click(self, window_name, obj_name):
        obj = self._get_object(window_name, obj_name)

        self._click_object(obj)

        return 1
    
    def xmlrpc_getobjectlist(self, window_name):
        obj_list = []
        for gui in list_guis(self._desktop):
            if match_name_to_acc(window_name, gui):
                for name, obj in appmap_pairs(gui):
                    obj_list.append(name)
                return obj_list

        raise LdtpServerException('Window does not exist')

    def xmlrpc_getobjectinfo(self, window_name, obj_name):
        obj = self._get_object(window_name, obj_name)

        props = ['child_index', 'key', 'obj_index', 'parent', 'class']

        # TODO: label and label_by, what else am I missing?
        return props
