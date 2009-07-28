'''
LDTP v2 utils.

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

import re
import gobject
import pyatspi
from re import match as re_match
from constants import abbreviated_roles
from fnmatch import translate as glob_trans
from server_exception import LdtpServerException

class Utils:
    cached_apps = None
    def __init__(self):
        lazy_load = True
        self._desktop = pyatspi.Registry.getDesktop(0)
        if Utils.cached_apps is None:
            pyatspi.Registry.registerEventListener(
                self._on_window_event, 'window')
            Utils.cached_apps = set()
            if lazy_load:
                for app in self._desktop:
                    if app is None: continue
                    self.cached_apps.add(app)

    def _on_window_event(self, event):
        self.cached_apps.add(event.host_application)

    def _list_guis(self):
        for app in self.cached_apps:
            if not app: continue
            try:
                for gui in app:
                    if not gui: continue
                    yield gui
            except LookupError:
                self.cached_apps.remove(app)

    def _ldtpize_accessible(self, acc):
        label_acc = None
        rel_set = acc.getRelationSet()
        if rel_set:
            for i, rel in enumerate(rel_set):
                if rel.getRelationType() == pyatspi.RELATION_LABELLED_BY:
                    label_acc = rel.getTarget(i)
                    break
        return abbreviated_roles.get(acc.getRole(), 'ukn'), \
            (label_acc or acc).name.replace(' ', '').rstrip(':.')

    def _glob_match(self, pattern, string):
        return bool(re_match(glob_trans(pattern), string))

    def _match_name_to_acc(self, name, acc):
        if acc.name == name:
            return 1
        _object_name = self._ldtpize_accessible(acc)
        _object_name = '%s%s' % (_object_name[0],_object_name[1])
        if _object_name  == name:
            return 1
        if self._glob_match(name, acc.name):
            return 1
        if self._glob_match(name, _object_name):
            return 1
        return 0

    def _match_name_to_appmap(self, name, appmap_name):
        """
        Required when object name has empty label
        """
        if name == appmap_name:
            return 1
        if self._glob_match(name, appmap_name):
            return 1
        return 0

    def _list_objects(self, obj):
        if obj:
            yield obj
            for child in obj:
                for c in self._list_objects(child):
                    yield c

    def _get_combo_child_object_type(self, obj):
        """
        This function will check for all levels and returns the first
        matching LIST / MENU type
        """
        if obj:
            for child in obj:
                if not child:
                    continue
                if child.childCount > 0:
                    child_obj = self._get_combo_child_object_type(child)
                    if child_obj:
                        return child_obj
                if child.getRole() == pyatspi.ROLE_LIST:
                    return child
                elif child.getRole() == pyatspi.ROLE_MENU:
                    return child

    def _get_child_object_type(self, obj, role_type):
        """
        This function will check for all levels and returns the first
        matching role_type
        """
        if obj and role_type:
            for child in obj:
                if not child:
                    continue
                if child.childCount > 0:
                    child_obj = self._get_child_object_type(child, role_type)
                    if child_obj:
                        return child_obj
                if child.getRole() == role_type:
                    return child

    def _appmap_pairs(self, gui):
        ldtpized_list = []
        for obj in self._list_objects(gui):
            abbrev_role, abbrev_name = self._ldtpize_accessible(obj)
            if abbrev_name == '':
                ldtpized_name_base = abbrev_role
                ldtpized_name = '%s0' % ldtpized_name_base
            else:
                ldtpized_name_base = '%s%s' % (abbrev_role,abbrev_name)
                ldtpized_name = ldtpized_name_base
            i = 1
            while ldtpized_name in ldtpized_list:
                ldtpized_name = '%s%d' % (ldtpized_name_base, i)
                i += 1
            ldtpized_list.append(ldtpized_name)
            yield ldtpized_name, obj

    def _get_menu_hierarchy(self, window_name, object_name):
        _menu_hierarchy = re.split(';', object_name)
        obj = self._get_object(window_name, _menu_hierarchy [0])
        for _menu in _menu_hierarchy[1:]:
            _flag = False
            for _child in self._list_objects(obj):
                if obj == _child:
                    # if the given object and child object matches
                    continue
                if self._match_name_to_acc(_menu, _child):
                    _flag = True
                    break
            if not _flag:
                raise LdtpServerException (
                    "Menu item %s doesn't exist in hierarchy" % _menu)
            obj = self._get_object(window_name, _menu)
        return obj

    def _click_object(self, obj, action = 'click'):
        try:
            iaction = obj.queryAction()
        except NotImplementedError:
            raise LdtpServerException(
                'Object does not have an Action interface')
        else:
            for i in xrange(iaction.nActions):
                if iaction.getName(i) == action:
                    iaction.doAction(i)
                    return
            raise LdtpServerException('Object does not have a "click" action')

    def _get_object(self, window_name, obj_name):
        for gui in self._list_guis():
            if self._match_name_to_acc(window_name, gui):
                for name, obj in self._appmap_pairs(gui):
                    if self._match_name_to_acc(obj_name, obj) or \
                            self._match_name_to_appmap(obj_name, name):
                        return obj
        raise LdtpServerException(
            'Unable to find object name in application map')

    def _grab_focus(self, obj):
        try:
            componenti = obj.queryComponent()
        except:
            raise LdtpServerException('Failed to grab focus for %s' % obj)
        componenti.grabFocus()

    def _get_accessible_at_row_column(self, obj, row_index, column_index):
        try:
            tablei = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('Object not table type.')

        if row_index < 0 or row_index > tablei.nRows:
            raise LdtpServerException('Row index out of range: %d' % row_index)

        if column_index < 0 or column_index > tablei.nColumns:
            raise LdtpServerException('Column index out of range: %d' % \
                                          column_index)

        cell = tablei.getAccessibleAt(row_index, column_index)
        if not cell:
            raise LdtpServerException('Unable to access table cell on ' \
                                          'the given row and column index')
        return cell

    def _check_state(self, obj, object_state):
        _state = obj.getState()
        _current_state = _state.getStates()

        _status = False
        if object_state in _current_state:
            _status = True

        return _status

    def _mouse_event(self, x, y, name = 'b1c'):
        pyatspi.Registry.generateMouseEvent(x, y, name)

        return 1

    def _get_size(self, obj):
        try:
            componenti = obj.queryComponent()
        except:
            raise LdtpServerException('Failed to grab focus for %s' % obj)
        return componenti.getExtents(pyatspi.DESKTOP_COORDS)
