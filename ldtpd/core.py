from pyatspi import findDescendant, Registry
import subprocess
from utils import ldtpize_accessible, \
    match_name_to_acc, list_guis, appmap_pairs
from constants import abbreviated_roles
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

class Ldtpd:
    '''
    Core LDTP class.
    '''
    def __init__(self):
        self._desktop = Registry.getDesktop(0)

    def isalive(self):
        return True

    def launchapp(self, cmdline):
        '''
        Launch application.

        @param cmdline: Command line string to execute.
        @type cmdline: string

        @return: PID of new process
        @rtype: integer

        @raise LdtpServerException: When command fails
        '''
        os.environ['NO_GAIL'] = '0'
        os.environ['NO_AT_BRIDGE'] = '0'
        try:
            process = subprocess.Popen(cmdline.split(' '))
        except Exception, e:
            raise LdtpServerException(str(e))
        os.environ['NO_GAIL'] = '1'
        os.environ['NO_AT_BRIDGE'] = '1'
        return process.pid

    def guiexist(self, window_name, object_name=''):
        '''
        Checks whether a window or component exists.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type object_name: string

        @return: 1 if GUI was found, 0 if not.
        @rtype: integer
        '''
        if object_name:
            waiter = ObjectExistsWaiter(window_name, object_name, 0)
        else:
            waiter = GuiExistsWaiter(window_name, 0)

        return int(waiter.run())

    def waittillguiexist(self, window_name, object_name='', timeout=5):
        '''
        Wait till a window or component exists.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type object_name: string
        @param timeout: Wait timeout in seconds
        @type timeout: integer

        @return: 1 if GUI was found, 0 if not.
        @rtype: integer
        '''
        if object_name:
            waiter = ObjectExistsWaiter(window_name, object_name, timeout)
        else:
            waiter = GuiExistsWaiter(window_name, timeout)

        return int(waiter.run())

    def waittillguinotexist(self, window_name, timeout=5):
        '''
        Wait till a window does not exist.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param timeout: Wait timeout in seconds
        @type timeout: integer

        @return: 1 if GUI has gone away, 0 if not.
        @rtype: integer
        '''
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
    def selectmenuitem(self, window_name, object_name):
        '''
        Select (click) a menu item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        self._click_object(obj)

        return 1

    def click(self, window_name, object_name):
        '''
        Click item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        self._click_object(obj)

        return 1
    
    def getobjectlist(self, window_name):
        '''
        Get list of items in given GUI.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: list of items in LDTP naming convention.
        @rtype: list
        '''
        obj_list = []
        for gui in list_guis(self._desktop):
            if match_name_to_acc(window_name, gui):
                for name, obj in appmap_pairs(gui):
                    obj_list.append(name)
                return obj_list

        raise LdtpServerException('Window does not exist')

    def getobjectinfo(self, window_name, object_name):
        '''
        Get object properties.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: list of properties
        @rtype: list
        '''
        obj = self._get_object(window_name, object_name)

        props = ['child_index', 'key', 'obj_index', 'parent', 'class']

        # TODO: label and label_by, what else am I missing?
        return props

    def getobjectproperty(self, window_name, object_name, prop):
        '''
        Get object property value.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param prop: property name.
        @type prop: string

        @return: list of properties
        @rtype: list
        '''
        if prop == 'child_index':
            obj = self._get_object(window_name, object_name)
            return obj.getIndexInParent()
        elif prop == 'key':
            obj = self._get_object(window_name, object_name) # A sanity check.
            return object_name # For now, we only match exact names anyway.
        elif prop == 'obj_index':
            role_count = {}
            for gui in list_guis(self._desktop):
                if match_name_to_acc(window_name, gui):
                    for name, obj in appmap_pairs(gui):
                        role = obj.getRole()
                        role_count[role] = role_count.get(role, 0) + 1
                        if name == object_name:
                            return '%s#%d' % (
                                abbreviated_roles.get(role, 'ukn'),
                                role_count.get(role, 1) - 1)

            raise LdtpServerException(
                'Unable to find object name in application map')
        elif prop == 'parent':
            cached_list = []
            for gui in list_guis(self._desktop):
                if match_name_to_acc(window_name, gui):
                    for name, obj in appmap_pairs(gui):
                        if name == object_name:
                            for pname, pobj in cached_list:
                                if obj in pobj: # avoid double link issues
                                    return pname
                            return ldtpize_accessible(obj.parent)
                        cached_list.insert(0, (name, obj))

            raise LdtpServerException(
                'Unable to find object name in application map')
        elif prop == 'class':
            obj = self._get_object(window_name, object_name)
            return obj.getRoleName()

        raise LdtpServerException('Unknown property "%s" in %s' % \
                                      (prop, object_name))

