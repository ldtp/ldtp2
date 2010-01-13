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
import pyatspi
import orderedset
from re import match as re_match
from constants import abbreviated_roles
from fnmatch import translate as glob_trans
from server_exception import LdtpServerException

class Utils:
    cached_apps = None
    def __init__(self):
        lazy_load = True
        self._callback = {}
        self._window_uptime = {}
        self._callback_event = []
        self._desktop = pyatspi.Registry.getDesktop(0)
        if Utils.cached_apps is None:
            pyatspi.Registry.registerEventListener(
                self._on_window_event, 'window')
            Utils.cached_apps = orderedset.OrderedSet()
            if lazy_load:
                for app in self._desktop:
                    if app is None: continue
                    self.cached_apps.add(app)

    def _on_window_event(self, event):
        self.cached_apps.add(event.host_application)

    def _list_apps(self):
        for app in list(self.cached_apps):
            if not app: continue
            yield app

    def _list_guis(self):
        for app in list(self.cached_apps):
            if not app: continue
            try:
                for gui in app:
                    if not gui: continue
                    yield gui
            except LookupError:
                self.cached_apps.discard(app)

    def _ldtpize_accessible(self, acc):
        label_acc = None
        rel_set = acc.getRelationSet()
        if rel_set:
            for i, rel in enumerate(rel_set):
                relationType = rel.getRelationType()
                if relationType == pyatspi.RELATION_LABELLED_BY or \
                        relationType == pyatspi.RELATION_CONTROLLED_BY:
                    label_acc = rel.getTarget(i)
                    break
        return abbreviated_roles.get(acc.getRole(), 'ukn'), \
            (label_acc or acc).name.replace(' ', '').rstrip(':.')

    def _glob_match(self, pattern, string):
        return bool(re_match(glob_trans(pattern), string, re.M | re.U | re.L))

    def _match_name_to_acc(self, name, acc):
        if acc.name == name:
            return 1
        _ldtpize_accessible_name = self._ldtpize_accessible(acc)
        _object_name = u'%s%s' % (_ldtpize_accessible_name[0],
                                  _ldtpize_accessible_name[1])
        if _object_name  == name:
            return 1
        if self._glob_match(name, acc.name):
            return 1
        if self._glob_match(name, _object_name):
            return 1
        role = acc.getRole()
        if role == pyatspi.ROLE_FRAME or role == pyatspi.ROLE_DIALOG or \
                role == pyatspi.ROLE_WINDOW or \
                role == pyatspi.ROLE_FONT_CHOOSER or \
                role == pyatspi.ROLE_FILE_CHOOSER or \
                role == pyatspi.ROLE_ALERT or \
                role == pyatspi.ROLE_COLOR_CHOOSER:
            strip = '( |\n)'
        else:
            strip = '( |:|\.|_|\n)'
        _tmp_name = re.sub(strip, '', name)
        if self._glob_match(_tmp_name, _object_name):
            return 1
        if self._glob_match(_tmp_name, _ldtpize_accessible_name[1]):
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
        ldtpized_obj_index = {}
        for obj in self._list_objects(gui):
            abbrev_role, abbrev_name = self._ldtpize_accessible(obj)
            if abbrev_role in ldtpized_obj_index:
                ldtpized_obj_index[abbrev_role] += 1
            else:
                ldtpized_obj_index[abbrev_role] = 0
            if abbrev_name == '':
                ldtpized_name_base = abbrev_role
                ldtpized_name = u'%s%d' % (ldtpized_name_base,
                                           ldtpized_obj_index[abbrev_role])
            else:
                ldtpized_name_base = u'%s%s' % (abbrev_role, abbrev_name)
                ldtpized_name = ldtpized_name_base
            i = 1
            while ldtpized_name in ldtpized_list:
                ldtpized_name = u'%s%d' % (ldtpized_name_base,
                                           i)
                i += 1
            ldtpized_list.append(ldtpized_name)
            yield ldtpized_name, obj, u'%s#%d' % (abbrev_role,
                                                  ldtpized_obj_index[abbrev_role])

    def _get_menu_hierarchy(self, window_name, object_name):
        _menu_hierarchy = re.split(';', object_name)
        # Get handle of menu
        obj = self._get_object(window_name, _menu_hierarchy[0])
        # Navigate all sub-menu under a menu
        for _menu in _menu_hierarchy[1:]:
            _flag = False
            for _child in self._list_objects(obj):
                if obj == _child:
                    # if the given object and child object matches
                    continue
                if self._match_name_to_acc(_menu, _child):
                    obj = _child
                    _flag = True
                    break
            if not _flag:
                raise LdtpServerException (
                    "Menu item %s doesn't exist in hierarchy" % _menu)
        return obj

    def _click_object(self, obj, action = 'click'):
        try:
            iaction = obj.queryAction()
        except NotImplementedError:
            raise LdtpServerException(
                'Object does not have an Action interface')
        else:
            for i in xrange(iaction.nActions):
                if re.match(action, iaction.getName(i)):
                    iaction.doAction(i)
                    return
            raise LdtpServerException('Object does not have a "click" action')

    def _get_window_handle(self, window_name):
        window_list = []
        window_type = {}

        # Search with accessible name
        for gui in self._list_guis():
            if self._match_name_to_acc(window_name, gui):
                return gui

        # Search with LDTP appmap format
        for gui in self._list_guis():
            w_name = self._ldtpize_accessible(gui)
            if w_name[1] == '':
                if w_name[0] in window_type:
                    window_type[w_name[0]] += 1
                else:
                    window_type[w_name[0]] = 0
                tmp_name = '%d' % window_type[w_name[0]]
            else:
                tmp_name = w_name[1]
            w_name = tmp_name = u'%s%s' % (w_name[0], tmp_name)
            index = 1
            while w_name in window_list:
                w_name = u'%s%d' % (tmp_name, index)
                index += 1
            window_list.append(w_name)
            if window_name == w_name:
                return gui
            if self._glob_match(window_name, w_name):
                return gui
            if self._glob_match(window_name, w_name):
                return gui
            if self._glob_match(re.sub(' ', '', window_name),
                                re.sub(' ', '', w_name)):
                return gui
        return None

    def _get_object(self, window_name, obj_name):
        _window_handle = self._get_window_handle(window_name)
        if not _window_handle:
            raise LdtpServerException('Unable to find window "%s"' % \
                                          window_name)
        for name, obj, obj_index in self._appmap_pairs(_window_handle):
            if self._glob_match(obj_name, obj_index) or \
                    self._match_name_to_acc(obj_name, obj) or \
                    self._match_name_to_appmap(obj_name, name):
                return obj
        raise LdtpServerException(
            'Unable to find object name "%s" in application map' % obj_name)

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
