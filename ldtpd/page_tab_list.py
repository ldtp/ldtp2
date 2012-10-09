"""
LDTP v2 Core Page Tab List.

@author: Eitan Isaacson <eitan@ascender.com>
@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@copyright: Copyright (c) 2009-12 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See "COPYING" in the source distribution for more information.

Headers in this file shall remain intact.
"""
import pyatspi 
from utils import Utils
from server_exception import LdtpServerException

class PageTabList(Utils):
    def selecttab(self, window_name, object_name, tab_name):
        """
        Select tab based on name.
        
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
        """
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
        """
        Select tab based on index.
        
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
        """
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
        """
        Verify tab name.
        
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
        """
        try:
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
                pass
        except:
            pass

        return 0

    def gettabcount(self, window_name, object_name):
        """
        Get tab count.
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: tab count on success.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)
        return obj.childCount

    def gettabname(self, window_name, object_name, tab_index):
        """
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
        """
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)
        if tab_index < 0 or tab_index > obj.childCount:
            raise LdtpServerException('Unable to get page tab name,' \
                                          ' invalid index')
        name = None

        try:
            child = obj.getChildAtIndex(int (tab_index))
            name = child.name
        except NotImplementedError:
            raise LdtpServerException('Not selectable object.')

        return name
