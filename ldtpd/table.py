'''
LDTP v2 Core Table.

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

class Table(Utils):
    def getrowcount(self, window_name, object_name):
        '''
        Get count of rows in table object.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: Number of rows.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            itable = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('object %s is not a table' % object_name)

        return itable.nRows

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
        @param column: Column index to get, default value 0
        @type column: index

        @return: cell value on success.
        @rtype: string
        '''
        obj = self._get_object(window_name, object_name)

        cell = self._get_accessible_at_row_column(obj, row_index, column)
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

    def checkrow(self, window_name, object_name, row_index, column = 0):
        '''
        Check row
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: index
        @param column: Column index to get, default value 0
        @type column: index

        @return: cell value on success.
        @rtype: string
        '''
        obj = self._get_object(window_name, object_name)

        cell = self._get_accessible_at_row_column(obj, row_index, column)
        flag = None
        if cell.childCount > 0:
            children = self._list_objects(cell)
            for child in children:
                try:
                    actioni = child.queryAction()
                    flag = True
                    if not self._check_state(child, pyatspi.STATE_CHECKED):
                        self._click_object(child, 'toggle')
                except NotImplementedError:
                    continue
                self._grab_focus(cell)
                break
        else:
            try:
                actioni = cell.queryAction()
                flag = True
                if not self._check_state(cell, pyatspi.STATE_CHECKED):
                    self._click_object(cell, 'toggle')
            except NotImplementedError:
                raise LdtpServerException('Unable to check row')
            self._grab_focus(cell)
        cell.unref()
        if not flag:
            raise LdtpServerException('Unable to check row')
        return 1

    def expandtablecell(self, window_name, object_name, row_index, column = 0):
        '''
        Expand or contract table cell
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: index
        @param column: Column index to get, default value 0
        @type column: index

        @return: cell value on success.
        @rtype: string
        '''
        obj = self._get_object(window_name, object_name)

        cell = self._get_accessible_at_row_column(obj, row_index, column)
        flag = None
        if cell.childCount > 0:
            children = self._list_objects(cell)
            for child in children:
                try:
                    actioni = child.queryAction()
                    flag = True
                    self._click_object(child, 'expand or contract')
                    self._grab_focus(cell)
                    break
                except NotImplementedError:
                    continue
        else:
            try:
                actioni = cell.queryAction()
                flag = True
                self._click_object(cell, 'expand or contract')
            except NotImplementedError:
                raise LdtpServerException('Unable to check row')
            self._grab_focus(cell)
        cell.unref()
        if not flag:
            raise LdtpServerException('Unable to check row')
        return 1

    def uncheckrow(self, window_name, object_name, row_index, column = 0):
        '''
        Check row
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: index
        @param column: Column index to get, default value 0
        @type column: index

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        cell = self._get_accessible_at_row_column(obj, row_index, column)
        flag = None
        if cell.childCount > 0:
            children = self._list_objects(cell)
            for child in children:
                try:
                    actioni = child.queryAction()
                    flag = True
                    if self._check_state(child, pyatspi.STATE_CHECKED):
                        self._click_object(child, 'toggle')
                except NotImplementedError:
                    continue
                self._grab_focus(cell)
                break
        else:
            try:
                actioni = cell.queryAction()
                flag = True
                if self._check_state(cell, pyatspi.STATE_CHECKED):
                    self._click_object(cell, 'toggle')
            except NotImplementedError:
                raise LdtpServerException('Unable to check row')
            self._grab_focus(cell)
        cell.unref()
        if not flag:
            raise LdtpServerException('Unable to check row')
        return 1

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

    def singleclickrow(self, window_name, object_name, row_text):
        '''
        Single click row matching given text
        
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
                            size = self._get_size(cell)
                            self._mouse_event(size.x + size.width / 2,
                                              size.y + size.height / 2,
                                              'b1c')
                            cell.unref()
                            return i
                elif self._match_name_to_acc(row_text, cell):
                    self._grab_focus(cell)
                    size = self._get_size(cell)
                    self._mouse_event(size.x + size.width / 2,
                                      size.y + size.height / 2,
                                      'b1c')
                    cell.unref()
                    return i
                cell.unref()
        raise LdtpServerException('Unable to get row index: %s' % row_text)

    def doubleclickrow(self, window_name, object_name, row_text):
        '''
        Single click row matching given text
        
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
                            size = self._get_size(cell)
                            self._mouse_event(size.x + size.width / 2,
                                              size.y + size.height / 2,
                                              'b1d')
                            cell.unref()
                            return i
                elif self._match_name_to_acc(row_text, cell):
                    self._grab_focus(cell)
                    size = self._get_size(cell)
                    self._mouse_event(size.x + size.width / 2,
                                      size.y + size.height / 2,
                                      'b1d')
                    cell.unref()
                    return i
                cell.unref()
        raise LdtpServerException('Unable to get row index: %s' % row_text)

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
        try:
            text = self.getcellvalue(window_name, object_name, row_index, column)
            return int(self._glob_match(row_text, text))
        except:
            return 0

    def doesrowexist(self, window_name, object_name, row_text):
        '''
        Verify table cell value with given text
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_text: Row text to match
        @type string

        @return: 1 on success 0 on failure.
        @rtype: integer
        '''
        try:
            obj = self._get_object(window_name, object_name)

            def _searchString(acc):
                try:
                    itext = acc.queryText()
                except NotImplementedError:
                    return False
                return row_text == itext.getText(0,-1)

            results = pyatspi.findDescendant(obj, _searchString)
        
            return int(bool(results))
        except:
            return 0

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
        try:
            text = self.getcellvalue(window_name, object_name, row_index, column)
            if re.search(row_text, text):
                return 1
        except:
            pass
        return 0
