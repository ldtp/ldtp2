'''
LDTP v2 Core Text.

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

import pyatspi 
from utils import Utils
from server_exception import LdtpServerException
from keypress_actions import TypeAction

class Text(Utils):
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
        if object_name:
            obj = self._get_object(window_name, object_name)
            self._grab_focus(obj)
        if data:
            for gui in self._list_guis():
                if self._match_name_to_acc(window_name, gui):
                    self._grab_focus(gui)

        data = data or window_name # TODO: Major hack, this is a bad API choice

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
        if obj.getRole() == pyatspi.ROLE_COMBO_BOX:
            obj = self._get_child_object_type(obj, pyatspi.ROLE_TEXT)
            if not obj:
                raise LdtpServerException('Unable to get combo box children')

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
        if obj.getRole() == pyatspi.ROLE_COMBO_BOX:
            child_obj = self._get_combo_child_object_type(obj)
            if child_obj.getRole() == pyatspi.ROLE_LIST:
                obj = self._get_child_object_type(obj, pyatspi.ROLE_TEXT)
                if not obj:
                    raise LdtpServerException('Unable to get text object')
            elif child_obj.getRole() == pyatspi.ROLE_MENU:
                return obj.name
            else:
                raise LdtpServerException('Unable to get combo box child object')
        try:
            texti = obj.queryText()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        return texti.getText(0, texti.characterCount)

    def verifypartialmatch(self, window_name, object_name, partial_text):
        '''
        Verify partial text
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param partial_text: Partial text to match
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        return int(self._glob_match(partial_text,
                                    self.gettextvalue(window_name,
                                                      object_name)))

    def verifysettext(self, window_name, object_name, text):
        '''
        Verify text is set correctly
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param text: text to match
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        return verifypartialmatch(window_name, object_name, text)

    def activatetext(self, window_name, object_name):
        '''
        Activate text
        
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
        self._grab_focus(obj)

        self._click_object(obj, 'activate')

        return 1

    def appendtext(self, window_name, object_name, data=''):
        '''
        Append string sequence.
        
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
        if obj.getRole() == pyatspi.ROLE_COMBO_BOX:
            obj = self._get_child_object_type(obj, pyatspi.ROLE_TEXT)
            if not obj:
                raise LdtpServerException('Unable to get combo box children')

        try:
            texti = obj.queryEditableText()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        print dir(texti)
        texti.setTextContents('%s%s' % (texti.getText(0, texti.characterCount),
                                        data.encode('utf-8')))
        return 1

    def istextstateenabled(self, window_name, object_name):
        '''
        Verifies text state enabled or not
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)
        return int(self._check_state(obj, pyatspi.STATE_EDITABLE))

    def getcharcount(self, window_name, object_name):
        '''
        Get character count
        
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
        self._grab_focus(obj)

        try:
            texti = obj.queryText()
        except NotImplementedError:
            raise LdtpServerException('Unable to get text.')

        return texti.characterCount

    def getcursorposition(self, window_name, object_name):
        '''
        Get cursor position
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: Cursor position on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            texti = obj.queryText()
        except NotImplementedError:
            raise LdtpServerException('Unable to get text.')

        return texti.caretOffset

    def setcursorposition(self, window_name, object_name, cursor_position):
        '''
        Set cursor position
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param cursor_position: Cursor position to be set
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            texti = obj.queryText()
        except NotImplementedError:
            raise LdtpServerException('Unable to get text.')

        texti.setCaretOffset(cursor_position)
        return 1

    def cuttext(self, window_name, object_name, start_position, end_position = -1):
        '''
        cut text from start position to end position
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param start_position: Start position
        @type object_name: integer
        @param end_position: End position, default -1
        Cut all the text from start position till end
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            texti = obj.queryEditableText()
        except NotImplementedError:
            raise LdtpServerException('Unable to get editable text.')

        if end_position == -1:
            end_position = texti.characterCount

        texti.cutText(start_position, end_position)

        return 1

    def copytext(self, window_name, object_name, start_position, end_position = -1):
        '''
        copy text from start position to end position
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param start_position: Start position
        @type object_name: integer
        @param end_position: End position, default -1
        Copy all the text from start position till end
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            texti = obj.queryEditableText()
        except NotImplementedError:
            raise LdtpServerException('Unable to get editable text.')

        if end_position == -1:
            end_position = texti.characterCount

        texti.copyText(start_position, end_position)

        return 1

    def deletetext(self, window_name, object_name, start_position, end_position = -1):
        '''
        delete text from start position to end position
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param start_position: Start position
        @type object_name: integer
        @param end_position: End position, default -1
        Delete all the text from start position till end
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            texti = obj.queryEditableText()
        except NotImplementedError:
            raise LdtpServerException('Unable to get editable text.')

        if end_position == -1:
            end_position = texti.characterCount

        texti.deleteText(start_position, end_position)

        return 1

    def pastetext(self, window_name, object_name, position = 0):
        '''
        paste text from start position to end position
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param position: Position to paste the text, default 0
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        try:
            texti = obj.queryEditableText()
        except NotImplementedError:
            raise LdtpServerException('Unable to get editable text.')

        texti.pasteText(position)

        return 1

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
