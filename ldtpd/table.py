"""
LDTP v2 Core Table.

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

See 'COPYING' in the source distribution for more information.

Headers in this file shall remain intact.
"""
import re
import pyatspi 
from utils import Utils
from server_exception import LdtpServerException

class Table(Utils):
    def getrowcount(self, window_name, object_name):
        """
        Get count of rows in table object.

        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: Number of rows.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)

        try:
            itable = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('object %s is not a table' % object_name)

        return itable.nRows

    def selectrow(self, window_name, object_name, row_text, partial_match=False):
        """
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
        """
        if partial_match:
            return self.selectrowpartialmatch(window_name, object_name, row_text)
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
                    flag = False
                    try:
                        if self._handle_table_cell:
                            # Was externally set, let us not
                            # touch this value
                            flag = True
                        else:
                            self._handle_table_cell = True
                        children = self._list_objects(cell)
                        for child in children:
                            if self._match_name_to_acc(row_text, child):
                                self._grab_focus(child)
                                return 1
                    finally:
                        if not flag:
                            self._handle_table_cell = False
                elif self._match_name_to_acc(row_text, cell):
                    self._grab_focus(cell)
                    return 1
        raise LdtpServerException('Unable to select row: %s' % row_text)

    def selectrowpartialmatch(self, window_name, object_name, row_text):
        """
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
        """
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
                    flag = False
                    try:
                        if self._handle_table_cell:
                            # Was externally set, let us not
                            # touch this value
                            flag = True
                        else:
                            self._handle_table_cell = True
                        children = self._list_objects(cell)
                        for child in children:
                            if re.search(row_text, child.name):
                                self._grab_focus(child)
                                return 1
                    finally:
                        if not flag:
                            self._handle_table_cell = False
                elif self._match_name_to_acc(row_text, cell):
                    self._grab_focus(cell)
                    return 1
        raise LdtpServerException('Unable to select row: %s' % row_text)

    def selectrowindex(self, window_name, object_name, row_index):
        """
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
        """
        obj = self._get_object(window_name, object_name)

        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        if row_index < 0 or row_index > tablei.nRows:
            raise LdtpServerException('Row index out of range: %d' % row_index)

        cell = tablei.getAccessibleAt(row_index, 0)
        self._grab_focus(cell)
        return 1

    def selectlastrow(self, window_name, object_name):
        """
        Select last row

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)

        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        cell = tablei.getAccessibleAt(tablei.nRows - 1, 0)
        self._grab_focus(cell)
        return 1

    def setcellvalue(self, window_name, object_name, row_index,
                     column = 0, data = None):
        """
        Set cell value

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: integer
        @param column: Column index to get, default value 0
        @type column: integer
        @param data: data, default value None
                None, used for toggle button
        @type data: string

        @return: 1 on success.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)

        cell = self._get_accessible_at_row_column(obj, row_index, column)
        print cell
        name = None
        if cell.childCount > 0:
            flag = False
            try:
                if self._handle_table_cell:
                    # Was externally set, let us not
                    # touch this value
                    flag = True
                else:
                    self._handle_table_cell = True
                children = self._list_objects(cell)
                for child in children:
                    try:
                        iaction = child.queryAction()
                    except NotImplementedError:
                        iaction = None
                    if iaction:
                        for i in xrange(iaction.nActions):
                            # If the cell is toggle type
                            if re.match('toggle', iaction.getName(i), re.I):
                                iaction.doAction(i)
                                self._grab_focus(child)
                                return 1
                            elif re.match('edit', iaction.getName(i), re.I):
                                try:
                                    texti = cell.queryEditableText()
                                except NotImplementedError:
                                    continue
                                self._grab_focus(child)
                                if not data:
                                    raise LdtpServerException('data cannot be empty string.')
                                return int(texti.setTextContents(data.encode('utf-8')))
                else:
                    raise LdtpServerException('Text cannot be entered into object.')
            finally:
                if not flag:
                    self._handle_table_cell = False
        else:
            try:
                iaction = cell.queryAction()
            except NotImplementedError:
                iaction = None
            self._grab_focus(cell)
            if iaction:
                for i in xrange(iaction.nActions):
                    # If the cell is toggle type
                    if re.match('toggle', iaction.getName(i), re.I):
                        iaction.doAction(i)
                        return 1
                    elif re.match('edit', iaction.getName(i), re.I):
                        try:
                            texti = cell.queryEditableText()
                        except NotImplementedError:
                            raise LdtpServerException('Text cannot be entered into object.')
                        if not data:
                            raise LdtpServerException('data cannot be empty string.')
                        return int(texti.setTextContents(data.encode('utf-8')))
        raise LdtpServerException('Text cannot be entered into object.')

    def getcellvalue(self, window_name, object_name, row_index, column = 0):
        """
        Get cell value

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: integer
        @param column: Column index to get, default value 0
        @type column: integer

        @return: cell value on success.
        @rtype: string
        """
        obj = self._get_object(window_name, object_name)

        cell = self._get_accessible_at_row_column(obj, row_index, column)
        name = None
        if cell.childCount > 0:
            flag = False
            try:
                if self._handle_table_cell:
                    # Was externally set, let us not
                    # touch this value
                    flag = True
                else:
                    self._handle_table_cell = True
                children = self._list_objects(cell)
                for child in children:
                    try:
                        texti = child.queryText()
                    except NotImplementedError:
                        continue
                    name = child.name
                    self._grab_focus(cell)
                    break
            finally:
                if not flag:
                    self._handle_table_cell = False
        else:
            name = cell.name
            self._grab_focus(cell)
        if not name:
            raise LdtpServerException('Unable to get row text')
        return name

    def getcellsize(self, window_name, object_name, row_index, column = 0):
        """
        Get cell size

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: integer
        @param column: Column index to get, default value 0
        @type column: integer

        @return: x, y, width, height on success.
        @rtype: list
        """
        obj=self._get_object(window_name, object_name)

        cell=self._get_accessible_at_row_column(obj, row_index, column)
        current_cell=None
        if cell.childCount > 0:
            flag = False
            try:
                if self._handle_table_cell:
                    # Was externally set, let us not
                    # touch this value
                    flag = True
                else:
                    self._handle_table_cell = True
                children = self._list_objects(cell)
                for child in children:
                    try:
                        texti = child.queryText()
                    except NotImplementedError:
                        continue
                    current_cell=child
                    self._grab_focus(cell)
                    break
            finally:
                if not flag:
                    self._handle_table_cell = False
        else:
            current_cell=cell
            self._grab_focus(cell)
        if not current_cell:
            raise LdtpServerException('Unable to find row and/or column')
        _coordinates=self._get_size(current_cell)
        return [_coordinates.x, _coordinates.y, \
                    _coordinates.width, _coordinates.height]

    def rightclick(self, window_name, object_name, row_text):
        """
        Right click on table cell

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_text: Row text to click
        @type row_text: string

        @return: 1 on success.
        @rtype: integer
        """
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
                    flag = False
                    try:
                        if self._handle_table_cell:
                            # Was externally set, let us not
                            # touch this value
                            flag = True
                        else:
                            self._handle_table_cell = True
                        children = self._list_objects(cell)
                        for child in children:
                            if self._match_name_to_acc(row_text, child):
                                self._grab_focus(child)
                                size = self._get_size(child)
                                self._mouse_event(size.x + size.width / 2,
                                                  size.y + size.height / 2, 'b3c')
                                return 1
                    finally:
                        if not flag:
                            self._handle_table_cell = False
                elif self._match_name_to_acc(row_text, cell):
                    self._grab_focus(cell)
                    size = self._get_size(cell)
                    self._mouse_event(size.x + size.width / 2,
                                      size.y + size.height / 2, 'b3c')
                    return 1
                
        raise LdtpServerException('Unable to right click row: %s' % row_text)

    def checkrow(self, window_name, object_name, row_index, column = 0):
        """
        Check row

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: integer
        @param column: Column index to get, default value 0
        @type column: integer

        @return: cell value on success.
        @rtype: string
        """
        obj = self._get_object(window_name, object_name)

        cell = self._get_accessible_at_row_column(obj, row_index, column)
        flag = None
        if cell.childCount > 0:
            flag = False
            try:
                if self._handle_table_cell:
                    # Was externally set, let us not
                    # touch this value
                    flag = True
                else:
                    self._handle_table_cell = True
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
            finally:
                if not flag:
                    self._handle_table_cell = False
        else:
            try:
                actioni = cell.queryAction()
                flag = True
                if not self._check_state(cell, pyatspi.STATE_CHECKED):
                    self._click_object(cell, 'toggle')
            except NotImplementedError:
                raise LdtpServerException('Unable to check row')
            self._grab_focus(cell)
        if not flag:
            raise LdtpServerException('Unable to check row')
        return 1

    def expandtablecell(self, window_name, object_name, row_index, column = 0):
        """
        Expand or contract table cell

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: integer
        @param column: Column index to get, default value 0
        @type column: integer

        @return: cell value on success.
        @rtype: string
        """
        obj = self._get_object(window_name, object_name)

        cell = self._get_accessible_at_row_column(obj, row_index, column)
        flag = None
        if cell.childCount > 0:
            flag = False
            try:
                if self._handle_table_cell:
                    # Was externally set, let us not
                    # touch this value
                    flag = True
                else:
                    self._handle_table_cell = True
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
            finally:
                if not flag:
                    self._handle_table_cell = False
        else:
            try:
                actioni = cell.queryAction()
                flag = True
                self._click_object(cell, 'expand or contract')
            except NotImplementedError:
                raise LdtpServerException('Unable to check row')
            self._grab_focus(cell)
        if not flag:
            raise LdtpServerException('Unable to check row')
        return 1

    def uncheckrow(self, window_name, object_name, row_index, column = 0):
        """
        Check row

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: integer
        @param column: Column index to get, default value 0
        @type column: integer

        @return: 1 on success.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)

        cell = self._get_accessible_at_row_column(obj, row_index, column)
        flag = None
        if cell.childCount > 0:
            flag = False
            try:
                if self._handle_table_cell:
                    # Was externally set, let us not
                    # touch this value
                    flag = True
                else:
                    self._handle_table_cell = True
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
            finally:
                if not flag:
                    self._handle_table_cell = False
        else:
            try:
                actioni = cell.queryAction()
                flag = True
                if self._check_state(cell, pyatspi.STATE_CHECKED):
                    self._click_object(cell, 'toggle')
            except NotImplementedError:
                raise LdtpServerException('Unable to check row')
            self._grab_focus(cell)
        if not flag:
            raise LdtpServerException('Unable to check row')
        return 1

    def gettablerowindex(self, window_name, object_name, row_text):
        """
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
        """
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
                    flag = False
                    try:
                        if self._handle_table_cell:
                            # Was externally set, let us not
                            # touch this value
                            flag = True
                        else:
                            self._handle_table_cell = True
                        children = self._list_objects(cell)
                        for child in children:
                            if self._match_name_to_acc(row_text, child):
                                self._grab_focus(child)
                                return i
                    finally:
                        if not flag:
                            self._handle_table_cell = False
                elif self._match_name_to_acc(row_text, cell):
                    self._grab_focus(cell)
                    return i
        raise LdtpServerException('Unable to get row index: %s' % row_text)

    def singleclickrow(self, window_name, object_name, row_text):
        """
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
        """
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
                    flag = False
                    try:
                        if self._handle_table_cell:
                            # Was externally set, let us not
                            # touch this value
                            flag = True
                        else:
                            self._handle_table_cell = True
                        children = self._list_objects(cell)
                        for child in children:
                            if self._match_name_to_acc(row_text, child):
                                self._grab_focus(child)
                                size = self._get_size(cell)
                                self._mouse_event(size.x + size.width / 2,
                                                  size.y + size.height / 2,
                                                  'b1c')
                                return i
                    finally:
                        if not flag:
                            self._handle_table_cell = False
                elif self._match_name_to_acc(row_text, cell):
                    self._grab_focus(cell)
                    size = self._get_size(cell)
                    self._mouse_event(size.x + size.width / 2,
                                      size.y + size.height / 2,
                                      'b1c')
                    return i
        raise LdtpServerException('Unable to get row index: %s' % row_text)

    def doubleclickrow(self, window_name, object_name, row_text):
        """
        Double click row matching given text

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
        """
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
                    flag = False
                    try:
                        if self._handle_table_cell:
                            # Was externally set, let us not
                            # touch this value
                            flag = True
                        else:
                            self._handle_table_cell = True
                        children = self._list_objects(cell)
                        for child in children:
                            if self._match_name_to_acc(row_text, child):
                                self._grab_focus(child)
                                size = self._get_size(cell)
                                self._mouse_event(size.x + size.width / 2,
                                                  size.y + size.height / 2,
                                                  'b1d')
                                return i
                    finally:
                        if not flag:
                            self._handle_table_cell = False
                elif self._match_name_to_acc(row_text, cell):
                    self._grab_focus(cell)
                    size = self._get_size(cell)
                    self._mouse_event(size.x + size.width / 2,
                                      size.y + size.height / 2,
                                      'b1d')
                    return i
        raise LdtpServerException('Unable to get row index: %s' % row_text)

    def verifytablecell(self, window_name, object_name, row_index,
                        column_index, row_text):
        """
        Verify table cell value with given text

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: integer
        @param column_index: Column index to get, default value 0
        @type column_index: integer
        @param row_text: Row text to match
        @type string

        @return: 1 on success 0 on failure.
        @rtype: integer
         """
        try:
            text = self.getcellvalue(window_name, object_name,
                                     row_index, column_index)
            return int(self._glob_match(row_text, text))
        except:
            return 0

    def doesrowexist(self, window_name, object_name, row_text,
                     partial_match = False):
        """
        Verify table cell value with given text

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_text: Row text to match
        @type string
        @param partial_match: Find partial match strings
        @type boolean

        @return: 1 on success 0 on failure.
        @rtype: integer
        """
        try:
            obj = self._get_object(window_name, object_name, False)

            def _searchString(acc):
                try:
                    itext = acc.queryText()
                except NotImplementedError:
                    return False
                if partial_match:
                    return bool(re.search(row_text, itext.getText(0, -1),
                                          re.M | re.U))
                else:
                    return row_text == itext.getText(0, -1)

            results = pyatspi.findDescendant(obj, _searchString)
        
            return int(bool(results))
        except:
            return 0

    def verifypartialtablecell(self, window_name, object_name, row_index,
                               column_index, row_text):
        """
        Verify partial table cell value

        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param row_index: Row index to get
        @type row_index: integer
        @param column_index: Column index to get, default value 0
        @type column_index: integer
        @param row_text: Row text to match
        @type string

        @return: 1 on success 0 on failure.
        @rtype: integer
        """
        try:
            text = self.getcellvalue(window_name, object_name, row_index, column)
            if re.search(row_text, text):
                return 1
        except:
            pass
        return 0
