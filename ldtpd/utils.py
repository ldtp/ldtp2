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

import os
import re
import pyatspi
from re import match as re_match
from constants import abbreviated_roles
from fnmatch import translate as glob_trans
from server_exception import LdtpServerException

class Utils:
    cached_apps = None
    def __init__(self):
        lazy_load = True
        self._states = {}
        self._appmap = {}
        self._callback = {}
        self._state_names = {}
        self._window_uptime = {}
        self._callback_event = []
        self._get_all_state_names()
        self._handle_table_cell = False
        self._desktop = pyatspi.Registry.getDesktop(0)
        if Utils.cached_apps is None:
            pyatspi.Registry.registerEventListener(
                self._on_window_event, 'window')
            Utils.cached_apps = list()
            if lazy_load:
                for app in self._desktop:
                    if app is None: continue
                    self.cached_apps.append(app)
        if os.environ.has_key('LDTP_DEBUG'):
            self._ldtp_debug = os.environ['LDTP_DEBUG']
        else:
            self._ldtp_debug = None

    def _get_all_state_names(self):
        """
        This is used by client internally to populate all states
        Create a dictionary
        """
        for state in pyatspi.STATE_VALUE_TO_NAME.keys():
            self._states[state.__repr__()] = state
            # Ignore STATE_ string for LDTPv1 compatibility
            self._state_names[state] = \
                state.__repr__().lower().partition("state_")[2]
        return self._states

    def _on_window_event(self, event):
        if event.host_application not in self.cached_apps:
            self.cached_apps.append(event.host_application)

    def _list_apps(self):
        for app in self.cached_apps:
            if not app: continue
            yield app

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
        label_by = label_acc = None
        rel_set = acc.getRelationSet()
        if rel_set:
            for i, rel in enumerate(rel_set):
                relationType = rel.getRelationType()
                if relationType == pyatspi.RELATION_LABELLED_BY or \
                        relationType == pyatspi.RELATION_CONTROLLED_BY:
                    label_acc = rel.getTarget(i)
                    break
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
        if label_acc:
            label_by = label_acc.name
        return abbreviated_roles.get(role, 'ukn'), \
            re.sub(strip, '', (label_acc or acc).name), \
            label_by

    def _glob_match(self, pattern, string):
        return bool(re_match(glob_trans(pattern), string, re.M | re.U | re.L))

    def _match_name_to_acc(self, name, acc):
        if acc.name == name:
            return 1
        _ldtpize_accessible_name = self._ldtpize_accessible(acc)
        _object_name = u'%s%s' % (_ldtpize_accessible_name[0],
                                  _ldtpize_accessible_name[1])
        if _object_name == name:
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

    def _match_name_to_appmap(self, name, acc):
        if self._glob_match(name, acc['key']):
            return 1
        if self._glob_match(name, acc['obj_index']):
            return 1
        if self._glob_match(name, acc['label_by']):
            return 1
        if self._glob_match(name, acc['label']):
            return 1
        # Strip space and look for object
        obj_name = u'%s' % re.sub(' ', '', name)
        role = acc['class']
        if role == 'frame' or role == 'dialog' or \
                role == 'window' or \
                role == 'font_chooser' or \
                role == 'file_chooser' or \
                role == 'alert' or \
                role == 'color_chooser':
            strip = '( |\n)'
        else:
            strip = '( |:|\.|_|\n)'
        obj_name = re.sub(strip, '', name)
        if acc['label_by']:
            _tmp_name = re.sub(strip, '', acc['label_by'])
            if self._glob_match(obj_name, _tmp_name):
                return 1
        if acc['label']:
            _tmp_name = re.sub(strip, '', acc['label'])
            if self._glob_match(obj_name, _tmp_name):
                return 1
        if self._glob_match(obj_name, acc['key']):
            return 1
        return 0

    def _list_objects(self, obj):
        if obj:
            yield obj
            for child in obj:
                if child.getRole() == pyatspi.ROLE_TABLE_CELL and \
                        not self._handle_table_cell:
                    # In OO.o navigating table cells consumes more time
                    # resource
                    break
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

    def _add_appmap_data(self, obj, parent):
        abbrev_role, abbrev_name, label_by = self._ldtpize_accessible(obj)
        if abbrev_role in self.ldtpized_obj_index:
            self.ldtpized_obj_index[abbrev_role] += 1
        else:
            self.ldtpized_obj_index[abbrev_role] = 0
        if abbrev_name == '':
            ldtpized_name_base = abbrev_role
            ldtpized_name = u'%s%d' % (ldtpized_name_base,
                                      self.ldtpized_obj_index[abbrev_role])
        else:
            ldtpized_name_base = u'%s%s' % (abbrev_role, abbrev_name)
            ldtpized_name = ldtpized_name_base
        i = 0
        while ldtpized_name in self.ldtpized_list:
            i += 1
            ldtpized_name = u'%s%d' % (ldtpized_name_base, i)
        if parent in self.ldtpized_list:
            self.ldtpized_list[parent]['children'].append(ldtpized_name)
        if not label_by:
            label_by = ''
        self.ldtpized_list[ldtpized_name] = {'key' : ldtpized_name,
                                             'parent' : parent,
                                             'class' : obj.getRoleName().replace(' ', '_'),
                                             'child_index' : obj.getIndexInParent(),
                                             'children' : [],
                                             'obj_index' : '%s#%d' % (abbrev_role,
                                                                      self.ldtpized_obj_index[abbrev_role]),
                                             'label' : obj.name,
                                             'label_by' : label_by,
                                             'description' : obj.description
                                             }
        return ldtpized_name

    def _populate_appmap(self, obj, parent, child_index):
        if obj:
            if child_index != -1:
                parent = self._add_appmap_data(obj, parent)
            for child in obj:
                if not child:
                    continue
                if child.getRole() == pyatspi.ROLE_TABLE_CELL:
                    break
                self._populate_appmap(child, parent, child.getIndexInParent())

    def _appmap_pairs(self, gui, force_remap = False):
        self.ldtpized_list = {}
        self.ldtpized_obj_index = {}
        if not force_remap:
            for key in self._appmap.keys():
                if self._match_name_to_acc(key, gui):
                    return self._appmap[key]
        abbrev_role, abbrev_name, label_by = self._ldtpize_accessible(gui)
        _window_name = u'%s%s' % (abbrev_role, abbrev_name)
        abbrev_role, abbrev_name, label_by = self._ldtpize_accessible(gui.parent)
        _parent = abbrev_name
        self._populate_appmap(gui, _parent, gui.getIndexInParent())
        self._appmap[_window_name] = self.ldtpized_list
        return self.ldtpized_list

    def _get_menu_hierarchy(self, window_name, object_name):
        _menu_hierarchy = re.split(';', object_name)
        if not re.search('^mnu', _menu_hierarchy[0]):
            _menu_hierarchy[0] = 'mnu%s' % _menu_hierarchy[0]
        obj = self._get_object(window_name, _menu_hierarchy[0])
        for _menu in _menu_hierarchy[1:]:
            _flag = False
            for _child in self._list_objects(obj):
                if obj == _child:
                    # if the given object and child object matches
                    continue
                if self._match_name_to_acc(_menu, _child):
                    _flag = True
                    obj = _child
                    break
            if not _flag:
                raise LdtpServerException (
                    'Menu item "%s" doesn\'t exist in hierarchy' % _menu)
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
            raise LdtpServerException('Object does not have a "%s" action' % action)

    def _get_object_in_window(self, appmap, obj_name):
        for name in appmap.keys():
            obj = appmap[name]
            if self._match_name_to_appmap(obj_name, obj):
                return obj
        return None

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
        appmap = self._appmap_pairs(_window_handle)
        obj = self._get_object_in_window(appmap, obj_name)
        if not obj:
            appmap = self._appmap_pairs(_window_handle, force_remap = True)
            obj = self._get_object_in_window(appmap, obj_name)
        if not obj:
            raise LdtpServerException(
                'Unable to find object name "%s" in application map' % obj_name)
        def _internal_get_object(window, obj_name, obj):
            """
            window: Window handle in pyatspi format
            obj_name: In appmap format
            obj: Current object hash index in appmap
            """
            def _traverse_parent(gui, window_name, obj, parent_list):
                """
                Traverse from current object to parent object, this is done
                later to get the object a11y handle from window to child object
                gui: Window handle
                window_name: Window name in appmap format
                obj: Current object hash index in appmap
                parent_list: List of object names in appmap format
                """
                if obj and window_name:
                    parent = obj['parent']
                    if parent not in appmap:
                        return parent_list
                    parent_list.append(parent)
                    if self._match_name_to_acc(parent, gui):
                        return parent_list
                    return _traverse_parent(gui, window_name,
                                            appmap[parent],
                                            parent_list)

            _parent_list = _traverse_parent(_window_handle, window_name, obj, [])
            if not _parent_list:
                raise LdtpServerException(
                    'Unable to find object name "%s" in application map' % obj_name)
            _parent_list.reverse()
            key = obj['key']
            if key:
                _parent_list.append(key)
            obj = _window_handle
            for key in _parent_list[1:]:
                _appmap_obj = appmap[key]
                _appmap_role = re.sub('_', ' ', _appmap_obj['class'])
                if key in appmap and obj:
                    tmp_obj = obj.getChildAtIndex(_appmap_obj['child_index'])
                    if not tmp_obj:
                        if obj.getRoleName() != _appmap_role:
                            # Traversing object role and appmap role doesn't match
                            if self._ldtp_debug:
                                print "Traversing object role and appmap role doesn't match"
                            return None
                        break
                    obj = tmp_obj
                    if obj.getRoleName() != _appmap_role:
                        # Traversing object role and appmap role doesn't match
                        if self._ldtp_debug:
                            print "Traversing object role and appmap role doesn't match"
                        return None
            return obj
        _current_obj = _internal_get_object(window_name, obj_name, obj)
        if not _current_obj:
            # retry once, before giving up
            appmap = self._appmap_pairs(_window_handle, force_remap = True)
            obj = self._get_object_in_window(appmap, obj_name)
            if not obj:
                raise LdtpServerException(
                    'Unable to find object name "%s" in application map' % obj_name)
            _current_obj = _internal_get_object(window_name, obj_name, obj)
        return _current_obj

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
