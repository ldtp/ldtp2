'''
LDTP v2 utils.

@author: Eitan Isaacson <eitan@ascender.com>
@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@copyright: Copyright (c) 2009-11 Nagappan Alagappan
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
import time
import logging
import pyatspi
import threading
import traceback
import logging.handlers
from re import match as re_match
from constants import abbreviated_roles
from fnmatch import translate as glob_trans
from server_exception import LdtpServerException

importStatGrab = False
try:
    import statgrab
    importStatGrab = True
except ImportError:
    pass

class LdtpCustomLog(logging.Handler):
    """
    Custom LDTP log, inherit logging.Handler and implement
    required API
    """
    def __init__(self):
        # Call base handler
        logging.Handler.__init__(self)
        # Log all the events in list
        self.log_events = []

    def emit(self, record):
        # Get the message and add to the list
        # Later the list element can be poped out
        self.log_events.append(u'%s-%s' % (record.levelname, record.getMessage()))

# Add LdtpCustomLog handler
logging.handlers.LdtpCustomLog = LdtpCustomLog
# Create instance of LdtpCustomLog handler
_custom_logger = logging.handlers.LdtpCustomLog()
# Set default log level as ERROR
_custom_logger.setLevel(logging.ERROR)
# Add handler to root logger
logger = logging.getLogger('')
# Add custom logger to the root logger
logger.addHandler(_custom_logger)

LDTP_LOG_MEMINFO = 60
LDTP_LOG_CPUINFO = 61
logging.addLevelName(LDTP_LOG_MEMINFO, 'MEMINFO')
logging.addLevelName(LDTP_LOG_CPUINFO, 'CPUINFO')

class ProcessStats(threading.Thread):
    """
    Capturing Memory and CPU Utilization statistics for an application and its related processes
    NOTE: You have to install python-statgrab package
    EXAMPLE USAGE:

    xstats = ProcessStats('evolution', 2)
    # Start Logging by calling start
    xstats.start()
    # Stop the process statistics gathering thread by calling the stopstats method
    xstats.stop()
    """

    def __init__(self, appname, interval = 2):
        """
        Start memory and CPU monitoring, with the time interval between
        each process scan

        @param appname: Process name, ex: firefox-bin.
        @type appname: string
        @param interval: Time interval between each process scan
        @type interval: float
        """
        if not importStatGrab:
            raise LdtpServerException('python-statgrab package is not installed')
        threading.Thread.__init__(self)
        self._appname = appname
        self._interval = interval
        self._stop = False
        self.running = True

    def __del__(self):
        self._stop = False
        self.running = False

    def get_cpu_memory_stat(self):
        proc_list = []
        for i in statgrab.sg_get_process_stats():
            if self._stop:
                self.running = False
                return proc_list
            # If len(i['process_name']) > 15, then the string is truncated by
            # statgrab module, so in re.search use i['process_name'] as search
            # criteria
            if not re.search(str(i['process_name']), self._appname,
                             re.U | re.L):
                # If process name doesn't match, continue
                continue
            # If process name matches
            # Get process title
            # ex output (string):
            # /usr/lib/gnome-panel/clock-applet --oaf-activate-iid= \
            #        OAFIID:GNOME_ClockApplet_Factory --oaf-ior-fd=32
            title = str(i['proctitle'])
            # Split the title to get exact string
            # ex output (list of string):
            # ['/usr/lib/gnome-panel/clock-applet',
            # '--oaf-activate-iid=OAFIID:GNOME_ClockApplet_Factory \
            #        --oaf-ior-fd=32 ']
            # Just split the first separater
            proctitle = re.split(" ", title, 1) # Split by space
            # ex output (list of string)
            # ['', 'usr', 'lib', 'gnome-panel', 'clock-applet']
             # Split by / and use the last string, which is process name
            procname = re.split("/", proctitle[0])[-1]
            if not re.match(self._appname, procname):
                # If process name and application name doesn't match
                # continue, don't add it to the list
                continue
            proc_list.append([i, procname])
        return proc_list

    def run(self):
        while not self._stop:
            for i, procname in self.get_cpu_memory_stat():
                # Add the stats into ldtp log
                # Resident memory will be in bytes, to convert it to MB
                # divide it by 1024*1024
                logger.log(LDTP_LOG_MEMINFO, '%s(%s) - %s' % \
                           (procname, str(i['pid']),
                            str(i['proc_resident'] / (1024*1024))))
                # CPU percent returned with 14 decimal values
                # ex: 0.0281199122531, round it to 2 decimal values
                # as 0.03
                logger.log(LDTP_LOG_CPUINFO, '%s(%s) - %s' % \
                           (procname, str(i['pid']),
                            str(round(i['cpu_percent'], 2))))
            # Wait for interval seconds before gathering stats again
            time.sleep(self._interval)

    def stop(self):
        self._stop = True
        self.running = False

class Utils:
    cached_apps = None
    def __init__(self):
        lazy_load = True
        self._states = {}
        self._appmap = {}
        self._callback = {}
        self._logger = logger
        self._state_names = {}
        self._window_uptime = {}
        self._callback_event = []
        self._get_all_state_names()
        self._handle_table_cell = False
        self._custom_logger = _custom_logger
        self._desktop = pyatspi.Registry.getDesktop(0)
        self._ldtp_debug = os.environ.get('LDTP_DEBUG', None)
        if Utils.cached_apps is None:
            pyatspi.Registry.registerEventListener(
                self._on_window_event, 'window')
            # Above window event doesn't get called for
            # 'window:destroy', so registering it individually
            pyatspi.Registry.registerEventListener(
                self._on_window_event, 'window:destroy')
            # Notify on any changes in all windows, based on this info,
            # its decided, whether force_remap is required or not
            pyatspi.Registry.registerEventListener(self._obj_changed, 
                                                   'object:children-changed')
            pyatspi.Registry.registerEventListener(
                self._obj_changed, 'object:property-change:accessible-name')

            Utils.cached_apps = list()
            if lazy_load:
                for app in self._desktop:
                    if app is None: continue
                    # app - Current open application a11y handle
                    # True - It has to appmap'ed on need basis
                    # (Means: On accessing window based on user request,
                    # force remap)
                    self.cached_apps.append([app, True])
        if self._ldtp_debug:
            _custom_logger.setLevel(logging.DEBUG)

    def _get_all_state_names(self):
        """
        This is used by client internally to populate all states
        Create a dictionary
        NOTE: Just called once, internally
        """
        for state in pyatspi.STATE_VALUE_TO_NAME.keys():
            self._states[state.__repr__()] = state
            # Ignore STATE_ string for LDTPv1 compatibility
            self._state_names[state] = \
                state.__repr__().lower().partition("state_")[2]
        return self._states

    def _obj_changed(self, event):
        """
        If window already in cached list, then mark for remap,
        as the children have changed
        """
        if self._ldtp_debug:
            print event, event.type, event.source, event.source.parent
        if not self.cached_apps:
            # If not initialized as list, don't process further
            return
        for app in self.cached_apps:
            try:
                if not app or not app[0] or app[0] != event.host_application:
                    continue
                # Force remap for this application, as some object is
                # either added / removed / changed
                index = self.cached_apps.index(app)
                self.cached_apps[index][1] = True
                # Just break, as the remap flag is set to true
                break
            except LookupError:
                # A11Y lookup error
                continue
            except ValueError:
                # Index error
                continue

    def _on_window_event(self, event):
        if self._ldtp_debug:
            print event, event.type, event.source, event.source.parent
        # Proceed only for window destry and deactivate event
        if event and (event.type == "window:destroy" or \
                          event.type == "window:deactivate") and \
                          event.source:
            abbrev_role, abbrev_name, label_by = self._ldtpize_accessible( \
                event.source)
            # LDTPized name
            win_name = u'%s%s' % (abbrev_role, abbrev_name)
            # Window title is empty
            if abbrev_name == '':
                for win_name in self._appmap.keys():
                    # When window doesn't have a title, destroy all the
                    # window info from appmap, which doesn't haven't title
                    if re.search('%s\d*$' % abbrev_role, win_name, re.M | re.U):
                        del self._appmap[win_name]
            else:
                for name in self._appmap.keys():
                    # When multiple window have same title, destroy all the
                    # window info from appmap, which have same title
                    if re.search('%s%s\d*$' % (abbrev_role, abbrev_name),
                                 win_name, re.M | re.U) or \
                                 re.search('%s%s*$' % (abbrev_role, abbrev_name),
                                           win_name, re.M | re.U):
                        del self._appmap[name]
            return
        cache = True
        if not self.cached_apps:
            # If not initialized as list, don't process further
            return
        for app in self.cached_apps:
            if event.host_application == app[0]:
                # Application already in cached list
                cache = False
                # Force remap for this application, as some object is
                # either added / removed / changed
                index = self.cached_apps.index(app)
                self.cached_apps[index][1] = True
                break
        if cache:
            # If app doesn't exist in cached apps, then add it
            # adding app and True flag as list - This flag indicates that the
            # object in application either got added / removed
            # so remap should be forced
            self.cached_apps.append([event.host_application, True])

    def _list_apps(self):
        """
        List all the applications
        """
        for app in self.cached_apps:
            if not app: continue
            yield app

    def _list_guis(self):
        """
        List all the windows that are currently open
        """
        for app in self.cached_apps:
            if not app or not app[0]: continue
            try:
                # application handle will be in app[0]
                # app[1] will hold, whether remap should be done or not
                for gui in app[0]:
                    if not gui: continue
                    yield gui
            except LookupError:
                # If the window doesn't exist, remove from the cached list
                self.cached_apps.remove(app)

    def _ldtpize_accessible(self, acc):
        """
        Get LDTP format accessibile name

        @param acc: Accessible handle
        @type acc: object

        @return: object type, stripped object name (associated / direct),
                        associated label
        @rtype: tuple
        """
        label_by = label_acc = None
        # Get accessible relation set
        rel_set = acc.getRelationSet()
        if rel_set:
            for i, rel in enumerate(rel_set):
                relationType = rel.getRelationType()
                # If object relation is labelled by or controlled by,
                # then give that importance, rather than the direct object label
                if relationType == pyatspi.RELATION_LABELLED_BY or \
                        relationType == pyatspi.RELATION_CONTROLLED_BY:
                    # Get associated label
                    label_acc = rel.getTarget(i)
                    break
        role = acc.getRole()
        if role == pyatspi.ROLE_FRAME or role == pyatspi.ROLE_DIALOG or \
                role == pyatspi.ROLE_WINDOW or \
                role == pyatspi.ROLE_FONT_CHOOSER or \
                role == pyatspi.ROLE_FILE_CHOOSER or \
                role == pyatspi.ROLE_ALERT or \
                role == pyatspi.ROLE_COLOR_CHOOSER:
            # Strip space and new line from window title
            strip = '( |\n)'
        else:
            # Strip space, colon, dot, underscore and new line from
            # all other object types
            strip = '( |:|\.|_|\n)'
        if label_acc:
            # Priority to associated label
            label_by = label_acc.name
        # Return the role type (if, not in the know list of roles,
        # return ukn - unknown), strip the above characters from name
        # also return labely_by string
        return abbreviated_roles.get(role, 'ukn'), \
            re.sub(strip, '', (label_acc or acc).name), \
            label_by

    def _glob_match(self, pattern, string):
        """
        Match given string, by escaping regex characters
        """
        # regex flags Multi-line, Unicode, Locale
        return bool(re_match(glob_trans(pattern), string,
                             re.M | re.U | re.L))

    def _match_name_to_acc(self, name, acc, classType = None):
        """
        Match given name with acc.name / acc.associate name
        and also class type

        @param name: Label to be matched
        @type name: string
        @param acc: Accessibility handle
        @type acc: object
        @param classType: role name
        @type classType: string

        @return: Return 0 on failure, 1 on successful match
        @rtype: integer
        """
        if not acc:
            return 0
        if classType:
            # Accessibility role type returns space, when multiple
            # words exist in object type. ex: 'push button'
            # User might mistype with multiple space, to avoid
            # any confusion, using _. So, user will be inputing
            # push_button
            roleName = acc.getRoleName().replace(' ', '_')
        else:
            roleName = None
        if roleName != classType:
            # If type doesn't match, don't proceed further
            return 0
        if acc.name == name:
            # Since, type already matched and now the given name
            # and accessibile name matched, mission accomplished
            return 1
        # Get LDTP format accessibile name
        _ldtpize_accessible_name = self._ldtpize_accessible(acc)
        # Concat object type and object name
        # ex: 'frmUnsavedDocument1-gedit' for Gedit application
        # frm - Frame, Window title - 'Unsaved Document 1 - gedit'
        _object_name = u'%s%s' % (_ldtpize_accessible_name[0],
                                  _ldtpize_accessible_name[1])
        if _object_name == name:
            # If given name equal LDTPized name format
            return 1
        if self._glob_match(name, acc.name):
            # If given name match object name with regexp
            return 1
        if self._glob_match(name, _object_name):
            # If given name match LDTPized name format with regexp
            return 1
        role = acc.getRole()
        if role == pyatspi.ROLE_FRAME or role == pyatspi.ROLE_DIALOG or \
                role == pyatspi.ROLE_WINDOW or \
                role == pyatspi.ROLE_FONT_CHOOSER or \
                role == pyatspi.ROLE_FILE_CHOOSER or \
                role == pyatspi.ROLE_ALERT or \
                role == pyatspi.ROLE_COLOR_CHOOSER:
            # If window type, strip using this format
            strip = '( |\n)'
        else:
            # If any other type, strip using this format
            strip = '( |:|\.|_|\n)'
        # Strip given name too, as per window type or other type
        _tmp_name = re.sub(strip, '', name)
        if self._glob_match(_tmp_name, _object_name):
            # Match stripped given name and LDTPized name
            return 1
        if self._glob_match(_tmp_name, _ldtpize_accessible_name[1]):
            # Match stripped given name and LDTPized name, without object type
            # ex: UnsavedDocument1-gedit, without frm at start
            return 1
        # If nothing matches, the search criteria fails, to find the object
        return 0

    def _match_name_to_appmap(self, name, acc):
        if not name:
            return 0
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
                if not self._handle_table_cell and \
                        child.getRole() == pyatspi.ROLE_TABLE_CELL:
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

    def _add_appmap_data(self, obj, parent, child_index):
        if not obj:
            return None
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
            _current_children = self.ldtpized_list[parent]['children']
            if _current_children:
                _current_children = u'%s %s' % (_current_children, ldtpized_name)
            else:
                _current_children = ldtpized_name
            self.ldtpized_list[parent]['children'] = _current_children
        if not label_by:
            label_by = ''
        self.ldtpized_list[ldtpized_name] = {'key' : ldtpized_name,
                                             'parent' : parent,
                                             'class' : obj.getRoleName().replace(' ', '_'),
                                             'child_index' : child_index,
                                             'children' : '',
                                             'obj_index' : '%s#%d' % (abbrev_role,
                                                                      self.ldtpized_obj_index[abbrev_role]),
                                             'label' : obj.name,
                                             'label_by' : label_by,
                                             'description' : obj.description
                                             }
        return ldtpized_name

    def _populate_appmap(self, obj, parent, child_index):
        index = -1
        if obj:
            if child_index != -1:
                parent = self._add_appmap_data(obj, parent, child_index)
            # Have noticed using obj.getIndexInParent()
            # returns -1, let the loop counts the child index
            for child in obj:
                index += 1
                if not child:
                    continue
                if child.getRole() == pyatspi.ROLE_TABLE_CELL:
                    break
                self._populate_appmap(child, parent, index)

    def _appmap_pairs(self, gui, window_name, force_remap = False):
        self.ldtpized_list = {}
        self.ldtpized_obj_index = {}
        if not force_remap:
            for app in self.cached_apps:
                try:
                    if app[0] and gui and app[0] == gui.parent and \
                            app[1] == True:
                        # Means force_remap
                        force_remap = True
                        index = self.cached_apps.index(app)
                        if index != -1:
                            # Reset force_remap to False
                            self.cached_apps[index][1] = False
                        break
                except NameError:
                    continue
            # If force_remap set in the above condition, skip the
            # following lookup and do force remap
            if not force_remap:
                for key in self._appmap.keys():
                    if self._match_name_to_acc(key, gui):
                        return self._appmap[key]

        if gui and gui.parent:
            abbrev_role, abbrev_name, label_by = self._ldtpize_accessible(gui.parent)
            _parent = abbrev_name
        else:
            _parent = ''
        self._populate_appmap(gui, _parent, gui.getIndexInParent())
        self._appmap[window_name] = self.ldtpized_list
        return self.ldtpized_list

    def _get_menu_hierarchy(self, window_name, object_name):
        _menu_hierarchy = re.split(';', object_name)
        if not re.search('^mnu', _menu_hierarchy[0], re.M | re.U):
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
                raise LdtpServerException(
                    'Menu item "%s" doesn\'t exist in hierarchy' % _menu)
        return obj

    def _click_object(self, obj, action = '(click|press|activate)'):
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
        """
        Get object in appmap dict format, eg: {'class' : 'menu', 'key': 'mnu0'}

        @param appmap: application map of window (list of dict)
        @type appmap: object
        @param obj_name: Object name
        @type obj_name: string

        @return: object in appmap dict format
        @rtype: object
        """
        for name in appmap.keys():
            obj = appmap[name]
            if self._match_name_to_appmap(obj_name, obj):
                return obj
        return None

    def _get_window_handle(self, window_name):
        """
        Get window handle of given window name

        @param window_name: window name, as provided by the caller
        @type window_name: string

        @return: window handle, window name in appmap format
        @rtype: object, string
        """
        window_list = []
        window_type = {}

        for gui in self._list_guis():
            if not gui:
                continue
            obj_name = self._ldtpize_accessible(gui)
            if obj_name[1] == '':
                # If label / label_by is empty string
                # use index
                if obj_name[0] in window_type:
                    # If the same window type repeats
                    # eg: multiple dialog window with empty title
                    # then use, dlg0, dlg1, dlg2 etc
                    window_type[obj_name[0]] += 1
                else:
                    # Initialize the first window in a type as 0
                    # and increment this counter
                    window_type[obj_name[0]] = 0
                tmp_name = '%d' % window_type[obj_name[0]]
            else:
                # If window has title, use that
                tmp_name = obj_name[1]
            # Append window type and window title
            w_name = name = '%s%s' % (obj_name[0], tmp_name)
            # If multiple window with same title, increment the index
            index = 1
            while name in window_list:
                # If window name already exist in list, increase
                # the index, so that we will have the window name
                # always unique
                name = '%s%d' % (w_name, index)
                index += 1
            window_list.append(name)

            if self._match_name_to_acc(window_name, gui):
                return gui, name

            # Search with LDTP appmap format
            if window_name == name:
                return gui, name
            if self._glob_match(window_name, name):
                return gui, name
            if self._glob_match(re.sub(' ', '', window_name),
                                re.sub(' ', '', name)):
                return gui, name
        return None, None

    def _get_object(self, window_name, obj_name):
        _window_handle, _window_name = \
            self._get_window_handle(window_name)
        if not _window_handle:
            raise LdtpServerException('Unable to find window "%s"' % \
                                          window_name)
        appmap = self._appmap_pairs(_window_handle, _window_name)
        obj = self._get_object_in_window(appmap, obj_name)
        if not obj:
            appmap = self._appmap_pairs(_window_handle, _window_name,
                                        force_remap = True)
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
                    if self._match_name_to_acc(parent, gui, appmap[parent]['class']):
                        return parent_list
                    return _traverse_parent(gui, window_name,
                                            appmap[parent],
                                            parent_list)

            if self._match_name_to_appmap(window_name, obj):
                # If window name and object name are same
                _parent_list = []
            else:
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
                                print "Traversing object role and appmap role " \
                                      "doesn't match", obj.getRoleName(), _appmap_role
                            return None
                        break
                    obj = tmp_obj
                    if obj.getRoleName() != _appmap_role:
                        # Traversing object role and appmap role doesn't match
                        if self._ldtp_debug:
                            print "Traversing object role and appmap role " \
                                  "doesn't match", obj.getRoleName(), _appmap_role
                        return None
            return obj
        _current_obj = _internal_get_object(window_name, obj_name, obj)
        if not _current_obj:
            # retry once, before giving up
            appmap = self._appmap_pairs(_window_handle, _window_name,
                                        force_remap = True)
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
