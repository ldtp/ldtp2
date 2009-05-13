'''
LDTP v2 Core.

@author: Eitan Isaacson <eitan@ascender.com>
@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@copyright: Copyright (c) 2009 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See "COPYING" in the source distribution for more information.

Headers in this file shall remain intact.
'''

from pyatspi import findDescendant, Registry
import locale
import subprocess
from utils import Utils
from constants import abbreviated_roles
from waiters import ObjectExistsWaiter, GuiExistsWaiter, \
    GuiNotExistsWaiter, NullWaiter
from keypress_actions import TypeAction
from server_exception import LdtpServerException
import os
import re
import pyatspi

class Ldtpd(Utils):
    '''
    Core LDTP class.
    '''
    def __init__(self):
        Utils.__init__(self)

    def isalive(self):
        return True

    def launchapp(self, cmd, args=[]):
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
            process = subprocess.Popen([cmd]+args)
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

    def waittillguiexist(self, window_name, object_name='', guiTimeOut=5):
        '''
        Wait till a window or component exists.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type object_name: string
        @param guiTimeOut: Wait timeout in seconds
        @type guiTimeOut: integer

        @return: 1 if GUI was found, 0 if not.
        @rtype: integer
        '''
        if object_name:
            waiter = ObjectExistsWaiter(window_name, object_name, guiTimeOut)
        else:
            waiter = GuiExistsWaiter(window_name, guiTimeOut)

        return int(waiter.run())

    def waittillguinotexist(self, window_name, guiTimeOut=5):
        '''
        Wait till a window does not exist.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param guiTimeOut: Wait timeout in seconds
        @type guiTimeOut: integer

        @return: 1 if GUI has gone away, 0 if not.
        @rtype: integer
        '''
        waiter = GuiNotExistsWaiter(window_name, guiTimeOut)

        return int(waiter.run())

    def getobjectsize(self, window_name, object_name):
        '''
        Get object size
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: x, y, width, height on success.
        @rtype: list
        '''
        obj = self._get_object(window_name, object_name)

        _coordinates = self._get_size(obj)
        return [_coordinates.x, _coordinates.y, \
                    _coordinates.width, _coordinates.height]

    def generatemouseevent(self, x, y, eventType = 'b1c'):
        '''
        Generate mouse event on x, y co-ordinates.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        return self._mouse_event(x, y, eventType)

    def mouseleftclick(self, window_name, object_name):
        '''
        Mouse left click on an object.
        
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

        self._grab_focus(obj)

        _coordinates = self._get_size(obj)
        return self._mouse_event(_coordinates.x + _coordinates.width / 2,
                                 _coordinates.y + _coordinates.height / 2,
                                 'b1c')

    def mouserightclick(self, window_name, object_name):
        '''
        Mouse right click on an object.
        
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

        self._grab_focus(obj)

        _coordinates = self._get_size(obj)
        return self._mouse_event(_coordinates.x + _coordinates.width / 2,
                                 _coordinates.y + _coordinates.height / 2,
                                 'b3c')

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
        if re.search(';', object_name):
            obj = self._get_menu_hierarchy(window_name, object_name)
        else:
            obj = self._get_object(window_name, object_name)

        self._click_object(obj)

        return 1

    def doesmenuitemexist(self, window_name, object_name):
        '''
        Check a menu item exist.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        try:
            if re.search(';', object_name):
                obj = self._get_menu_hierarchy(window_name, object_name)
            else:
                obj = self._get_object(window_name, object_name)
            return 1
        except:
            return 0

    def listsubmenus(self, window_name, object_name):
        '''
        List children of menu item
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: menu item in ';' separated format on success.
        @rtype: string
        '''
        if re.search(';', object_name):
            obj = self._get_menu_hierarchy(window_name, object_name)
        else:
            obj = self._get_object(window_name, object_name)
        _children = ''
        for _child in self._list_objects (obj):
            if _child.name == '' or _child.name == 'Empty' or \
                    obj == _child:
                # If empty string don't add it to the list or
                # if the given object and child object matches
                continue
            if _children == '':
                _children += _child.name
            else:
                _children += ';%s' % _child.name
        return _children

    def menucheck(self, window_name, object_name):
        '''
        Check (click) a menu item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        if re.search(';', object_name):
            obj = self._get_menu_hierarchy(window_name, object_name)
        else:
            obj = self._get_object(window_name, object_name)

        if self._check_state(obj, pyatspi.STATE_CHECKED) == False:
            self._click_object(obj)

        return 1

    def menuuncheck(self, window_name, object_name):
        '''
        Check (click) a menu item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        if re.search(';', object_name):
            obj = self._get_menu_hierarchy(window_name, object_name)
        else:
            obj = self._get_object(window_name, object_name)

        if self._check_state(obj, pyatspi.STATE_CHECKED):
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
    
    def press(self, window_name, object_name):
        '''
        Press item.
        
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

        self._click_object(obj, 'press')

        return 1
    
    def invokemenu(self, window_name, object_name):
        '''
        Invoke menu item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        return self.press (window_name, object_name)

    def check(self, window_name, object_name):
        '''
        Check item.
        
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

        if self._check_state(obj, pyatspi.STATE_CHECKED) == False:
            self._click_object(obj)

        return 1

    def uncheck(self, window_name, object_name):
        '''
        Uncheck item.
        
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

        if self._check_state(obj, pyatspi.STATE_CHECKED):
            self._click_object(obj)

        return 1
    
    def verifytoggled(self, window_name, object_name):
        '''
        Verify toggle item toggled.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        '''
        return self.verifycheck(window_name, object_name)

    def verifycheck(self, window_name, object_name):
        '''
        Verify check item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        return int(self._check_state(obj, pyatspi.STATE_CHECKED))

    def verifyuncheck(self, window_name, object_name):
        '''
        Verify uncheck item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        return int(not self._check_state(obj, pyatspi.STATE_CHECKED))

    def stateenabled(self, window_name, object_name):
        '''
        Check whether an object state is enabled or not
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        return int(self._check_state(obj, pyatspi.STATE_ENABLED))

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
        for gui in self._list_guis():
            if self._match_name_to_acc(window_name, gui):
                for name, obj in self._appmap_pairs(gui):
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
            for gui in self._list_guis():
                if self._match_name_to_acc(window_name, gui):
                    for name, obj in self._appmap_pairs(gui):
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
            for gui in self._list_guis():
                if self._match_name_to_acc(window_name, gui):
                    for name, obj in self._appmap_pairs(gui):
                        if name == object_name:
                            for pname, pobj in cached_list:
                                if obj in pobj: # avoid double link issues
                                    return pname
                            _parent = self._ldtpize_accessible(obj.parent)
                            return '%s%s' % (_parent[0], _parent[1])
                        cached_list.insert(0, (name, obj))

            raise LdtpServerException(
                'Unable to find object name in application map')
        elif prop == 'class':
            obj = self._get_object(window_name, object_name)
            return obj.getRoleName().replace(' ', '_')

        raise LdtpServerException('Unknown property "%s" in %s' % \
                                      (prop, object_name))

    def getchild(self, window_name, child_name='', role=''):
        '''
        Gets the list of object available in the window, which matches 
        component name or role name or both.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param child_name: Child name to search for.
        @type child_name: string
        @param role: role name to search for, or an empty string for wildcard.
        @type role: string

        @return: list of matched children names
        @rtype: list
        '''
        matches = []
        for gui in self._list_guis():
            if self._match_name_to_acc(window_name, gui):
                for name, obj in self._appmap_pairs(gui):
                    if child_name and role:
                        if obj.getRoleName() == role and \
                                (child_name == name or \
                                     self._match_name_to_acc(child_name, obj)):
                            matches.append(name)
                    elif role:
                        if obj.getRoleName() == role:
                            matches.append(name)
                    elif child_name:
                        if child_name == name or \
                                self._match_name_to_acc(child_name, obj):
                            matches.append(name)
                
        if not matches:
            raise LdtpServerException('Could not find a child.')

        return matches

    def remap(self, window_name):
        '''
        For backwards compatability, does not do anything since we are entirely
        dynamic.

        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1
        @rtype: integer
        '''
        return 1

    def wait(self, timeout=5):
        '''
        Wait a given amount of seconds.

        @param timeout: Wait timeout in seconds
        @type timeout: integer

        @return: 1
        @rtype: integer
        '''
        waiter = NullWaiter(1, timeout)

        return waiter.run()

    def enterstring(self, window_name, object_name='', data=''):
        '''
        Type string sequence.
        
        @param window_name: Window name to focus on, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to focus on, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param data: data to type.
        @type data: string

        @return: 1 on success.
        @rtype: integer
        '''
        if data and object_name:
            obj = self._get_object(window_name, object_name)
            self._grab_focus(obj)
        if data:
            for gui in self._list_guis():
                if self._match_name_to_acc(window_name, gui):
                    self._grab_focus(gui)

        type_action = TypeAction(data)
        type_action()

        return 1

    def settextvalue(self, window_name, object_name, data=''):
        '''
        Type string sequence.
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param data: data to type.
        @type data: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            texti = obj.queryEditableText()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        return int(texti.setTextContents(data.encode('utf-8')))

    def gettextvalue(self, window_name, object_name):
        '''
        Get text value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: text on success.
        @rtype: string
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            texti = obj.queryText()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        return texti.getText(0, texti.characterCount)

    def selectrow(self, window_name, object_name, row_text):
        '''
        Select row
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_text: Row text to select
        @type row_text: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        for i in range(0, tablei.nRows):
            for j in range(0, tablei.nColumns):
                cell = tablei.getAccessibleAt(i, j)
                if not cell:
                    continue
                if cell.childCount > 0:
                    children = self._list_objects(cell)
                    for child in children:
                        if self._match_name_to_acc(row_text, child):
                            self._grab_focus(child)
                            cell.unref()
                            return 1
                elif self._match_name_to_acc(row_text, cell):
                        self._grab_focus(cell)
                        cell.unref()
                        return 1
                cell.unref()
        raise LdtpServerException('Unable to select row: %s' % row_text)

    def selectrowpartialmatch(self, window_name, object_name, row_text):
        '''
        Select row partial match
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_text: Row text to select
        @type row_text: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        for i in range(0, tablei.nRows):
            for j in range(0, tablei.nColumns):
                cell = tablei.getAccessibleAt(i, j)
                if not cell:
                    continue
                if cell.childCount > 0:
                    children = self._list_objects(cell)
                    for child in children:
                        if re.search(row_text, child.name):
                            self._grab_focus(child)
                            cell.unref()
                            return 1
                elif self._match_name_to_acc(row_text, cell):
                        self._grab_focus(cell)
                        cell.unref()
                        return 1
                cell.unref()
        raise LdtpServerException('Unable to select row: %s' % row_text)

    def selectrowindex(self, window_name, object_name, row_index):
        '''
        Select row index
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to select
        @type row_index: integer

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        if row_index < 0 or row_index > tablei.nRows:
            raise LdtpServerException('Row index out of range: %d' % row_index)

        cell = tablei.getAccessibleAt(row_index, 0)
        self._grab_focus(cell)
        cell.unref()
        return 1

    def selectlastrow(self, window_name, object_name):
        '''
        Select last row
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        cell = tablei.getAccessibleAt(tablei.nRows - 1, 0)
        self._grab_focus(cell)
        cell.unref()
        return 1

    def getcellvalue(self, window_name, object_name, row_index, column = 0):
        '''
        Get cell value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: index
        @param column_index: Column index to get, default value 0
        @type column_index: index

        @return: cell value on success.
        @rtype: string
        '''
        obj = self._get_object(window_name, object_name)

        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        if row_index < 0 or row_index > tablei.nRows:
            raise LdtpServerException('Row index out of range: %d' % row_index)

        if column < 0 or column > tablei.nColumns:
            raise LdtpServerException('Column index out of range: %d' % column)

        cell = tablei.getAccessibleAt(row_index, column)
        if not cell:
            raise LdtpServerException('Unable to access table cell on ' \
                                          'the given row and column index')
        name = None
        if cell.childCount > 0:
            children = self._list_objects(cell)
            for child in children:
                try:
                    texti = child.queryText()
                except NotImplementedError:
                    continue
                name = child.name
                self._grab_focus(cell)
                break
        else:
            name = cell.name
            self._grab_focus(cell)
        cell.unref()
        if not name:
            raise LdtpServerException('Unable to get row text')
        return name

    def getaccessible(self, window_name, object_name):
        '''
        Get table row index matching given text
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: accessible handle on success.
        @rtype: Accessible handle
        '''
        return self._get_object(window_name, object_name)

    def gettablerowindex(self, window_name, object_name, row_text):
        '''
        Get table row index matching given text
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_text: Row text to select
        @type row_text: string

        @return: row index matching the text on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        for i in range(0, tablei.nRows):
            for j in range(0, tablei.nColumns):
                cell = tablei.getAccessibleAt(i, j)
                if not cell:
                    continue
                if cell.childCount > 0:
                    children = self._list_objects(cell)
                    for child in children:
                        if self._match_name_to_acc(row_text, child):
                            self._grab_focus(child)
                            cell.unref()
                            return i
                elif self._match_name_to_acc(row_text, cell):
                        self._grab_focus(cell)
                        cell.unref()
                        return i
                cell.unref()
        raise LdtpServerException('Unable to get row index: %s' % row_text)

    def getrowcount(self, window_name, object_name):
        '''
        Select row partial match
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: Row count on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        return tablei.nRows

    def verifytablecell(self, window_name, object_name, row_index,
                        column_index, row_text):
        '''
        Verify table cell value with given text
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: index
        @param column_index: Column index to get, default value 0
        @type column_index: index
        @param row_text: Row text to match
        @type string

        @return: 1 on success 0 on failure.
        @rtype: integer
         '''
        text = self.getcellvalue(window_name, object_name, row_index, column)
        return int(self._glob_match(row_text, text))

    def verifypartialtablecell(self, window_name, object_name, row_index,
                               column_index, row_text):
        '''
        Verify partial table cell value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: index
        @param column_index: Column index to get, default value 0
        @type column_index: index
        @param row_text: Row text to match
        @type string

        @return: 1 on success 0 on failure.
        @rtype: integer
        '''
        text = self.getcellvalue(window_name, object_name, row_index, column)
        if re.search(row_text, text):
            return 1
        else:
            return 0

    def selecttab(self, window_name, object_name, tab_name):
        '''
        Verify table cell value with given text
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param tab_name: tab to select
        @type data: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            index = 0
            for child in obj:
                if not child:
                    index += 1
                    continue
                if self._match_name_to_acc(tab_name, child):
                    if self._check_state(child, pyatspi.STATE_SELECTED):
                        # Pag tab already selected
                        return 1
                    else:
                        selectioni = obj.querySelection()
                        selectioni.selectChild(index)
                        return 1
                index += 1
        except NotImplementedError:
            raise LdtpServerException('Unable to select page tab object.')

        raise LdtpServerException('Page tab name does not exist')

    def selecttabindex(self, window_name, object_name, tab_index):
        '''
        Type string sequence.
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param tab_index: tab to select
        @type data: integer

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)
        if tab_index < 0 or tab_index > obj.childCount:
            raise LdtpServerException('Unable to get page tab name,' \
                                          ' invalid index')

        try:
            selectioni = obj.querySelection()
            selectioni.selectChild(tab_index)
            return 1
        except NotImplementedError:
            raise LdtpServerException('Unable to select page tab object.')

        raise LdtpServerException('Page tab index does not exist')

    def verifytabname(self, window_name, object_name, tab_name):
        '''
        Type string sequence.
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param tab_name: tab to select
        @type data: string

        @return: 1 on success 0 on failure
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            for child in obj:
                if not child:
                    continue
                if self._match_name_to_acc(tab_name, child) and \
                        self._check_state(child, pyatspi.STATE_SELECTED):
                    return 1
        except NotImplementedError:
            raise LdtpServerException('Unable to select page tab object.')

        return 0

    def gettabcount(self, window_name, object_name):
        '''
        Type string sequence.
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: tab count on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)
        return obj.childCount

    def gettabname(self, window_name, object_name, tab_index):
        '''
        Get tab name
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param tab_index: Index of tab (zero based index)
        @type object_name: int

        @return: text on success.
        @rtype: string
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)
        if tab_index < 0 or tab_index > obj.childCount:
            raise LdtpServerException('Unable to get page tab name,' \
                                          ' invalid index')
        name = None

        try:
            child = obj.getChildAtIndex(int (tab_index))
            name = child.name
            child.unref()
        except NotImplementedError:
            raise LdtpServerException('Not selectable object.')

        return name

    def getstatusbartext(self, window_name, object_name):
        '''
        Get text value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: text on success.
        @rtype: string
        '''
        return self.gettextvalue(window_name, object_name)

    def setvalue(self, window_name, object_name, data):
        '''
        Type string sequence.
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param data: data to type.
        @type data: double

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        valuei.currentValue = float (data)
        return 1

    def getvalue(self, window_name, object_name):
        '''
        Get object value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: value on success.
        @rtype: float
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        return valuei.currentValue

    def verifysetvalue(self, window_name, object_name, data):
        '''
        Get object value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param data: data to verify.
        @type data: double

        @return: 1 on success 0 on failure.
        @rtype: 1
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        if valuei.currentValue == data:
            return 1
        else:
            return 0

    def getminvalue(self, window_name, object_name):
        '''
        Get object min value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: float value on success.
        @rtype: float
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        return valuei.minimumValue

    def getminincrement(self, window_name, object_name):
        '''
        Get object min increment value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: float value on success.
        @rtype: float
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        return valuei.minimumIncrement

    def getmaxvalue(self, window_name, object_name):
        '''
        Get object max value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: float value on success.
        @rtype: float
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        return valuei.maximumValue

    def setlocale(self, locale_str):
        '''
        Set the locale to the given value.

        @param locale_str: locale to set to.
        @type locale_str: string

        @return: 1
        @rtype: integer
        '''
        locale.setlocale(locale.LC_ALL, locale_str)
        return 1
