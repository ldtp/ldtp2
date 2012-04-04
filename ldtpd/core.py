# -*- coding: utf-8 -*-
"""
LDTP v2 Core.

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

wnckModule = False
from pyatspi import findDescendant, Registry
import locale
import subprocess
try:
  # If we have gtk3+ gobject introspection, use that
  from gi.repository import Wnck as wnck
  from gi.repository import Gtk as gtk
  from gi.repository import Gdk as gdk
  wnckModule = gtk3 = True
except:
  # No gobject introspection, use gtk2 libwnck
  import gtk
  try:
    import wnck
    wnckModule = True
  except:
    # Not all environments support wnck package
    pass
  gtk3 = False
from utils import Utils, ProcessStats
from constants import abbreviated_roles
from keypress_actions import KeyboardOp
from waiters import ObjectExistsWaiter, GuiExistsWaiter, \
    GuiNotExistsWaiter, ObjectNotExistsWaiter, NullWaiter, \
    MaximizeWindow, MinimizeWindow, UnmaximizeWindow, UnminimizeWindow, \
    ActivateWindow, CloseWindow
from server_exception import LdtpServerException
import os
import re
import sys
import time
import pyatspi
import traceback
from fnmatch import translate as glob_trans

from menu import Menu
from text import Text
from mouse import Mouse
from table import Table
from value import Value
from generic import Generic
from combo_box import ComboBox
from page_tab_list import PageTabList

class Ldtpd(Utils, ComboBox, Table, Menu, PageTabList,
            Text, Mouse, Generic, Value):
    """
    Core LDTP class.
    """
    def __init__(self):
        Utils.__init__(self)
        # Window up time and onwindowcreate events
        self._events = ["window:create", "window:destroy"]
        # Registered keyboard events
        self._kb_timestamp = None
        self._kb_entries = []
        self._kb_modifiers = []
        # User registered events
        self._registered_events = []
        pyatspi.Registry.registerEventListener(self._event_cb, *self._events)
        self._process_stats = {}

    def __del__(self):
        if '_events' in dir(self):
            # De-register all registered events
          try:
            pyatspi.Registry.deregisterEventListener(self._event_cb, *self._events)
            pyatspi.Registry.deregisterEventListener(self._registered_event_cb,
                                                     *self._registered_events)
          except AttributeError:
            # Handle exception during cleanup
            pass
        for key in self._process_stats.keys():
            # Stop all process monitoring instances
            self._process_stats[key].stop()

    def _registered_event_cb(self, event):
      try:
        if event and event.source and event.type:
            abbrev_role, abbrev_name, label_by = self._ldtpize_accessible( \
                event.source)
            window_name = u'%s%s' % (abbrev_role, abbrev_name)
            self._callback_event.append(u"%s-%s" % (event.type, window_name))
      except:
        if self._ldtp_debug:
          print traceback.format_exc()

    def _registered_kb_event_cb(self, event):
        if not event:
            return
        if event.timestamp == self._kb_timestamp:
            # If multiple keyboard events registered
            # then multiple times, the callback is called
            # but with same timestamp, so let us ignore the
            # repeated callbacks
            return
        # Store the current timestamp
        self._kb_timestamp = event.timestamp
        if event.modifiers in self._kb_modifiers and \
               event.hw_code in self._kb_entries:
            self._callback_event.append(u"kbevent-%s-%d" % (event.event_string,
                                                            event.modifiers))

    def _event_cb(self, event):
      try:
        if event and event.type == "window:create" and event.source:
            for window in self._callback:
                if window and self._match_name_to_acc(window, event.source):
                    self._callback_event.append(u"onwindowcreate-%s" % window)
            abbrev_role, abbrev_name, label_by = self._ldtpize_accessible( \
                event.source)
            win_name = u'%s%s' % (abbrev_role, abbrev_name)
            self._window_uptime[win_name] = [event.source_name,
                                             time.strftime("%Y %m %d %H %M %S")]
        elif event and event.type == "window:destroy" and event.source:
            abbrev_role, abbrev_name, label_by = self._ldtpize_accessible( \
                event.source)
            win_name = u'%s%s' % (abbrev_role, abbrev_name)
            if win_name in self._window_uptime:
                self._window_uptime[win_name].append( \
                    time.strftime("%Y %m %d %H %M %S"))
      except:
        if self._ldtp_debug:
          print traceback.format_exc()

    def getapplist(self):
        """
        Get all accessibility application name that are currently running
        
        @return: list of appliction name of string type on success.
        @rtype: list
        """
        app_list = []
        for app in self._list_apps():
            try:
                app = app[0] # Just use the application handle
                if app.name != '<unknown>':
                    app_list.append(app.name)
            except LookupError:
                # A11Y lookup error
                continue
        return app_list

    def getwindowlist(self):
        """
        Get all accessibility window that are currently open
        
        @return: list of window names in LDTP format of string type on success.
        @rtype: list
        """
        window_list = []
        window_type = {}
        for gui in self._list_guis():
            if not gui:
                continue
            window_name = self._ldtpize_accessible(gui)
            if window_name[1] == '':
                if window_name[0] in window_type:
                    window_type[window_name[0]] += 1
                else:
                    window_type[window_name[0]] = 0
                tmp_name = '%d' % window_type[window_name[0]]
            else:
                tmp_name = window_name[1]
            w_name = window_name = '%s%s' % (window_name[0], tmp_name)
            index = 1
            while window_name in window_list:
                window_name = '%s%d' % (w_name, index)
                index += 1
            window_list.append(window_name)
        return window_list

    def isalive(self):
        return True

    def handletablecell(self):
        self._handle_table_cell = True
        return 1

    def unhandletablecell(self):
        self._handle_table_cell = False
        return 1

    def delaycmdexec(self, delay = None):
        """
        Delay command execution

        @param delay: Delay after the application is launched
        @type delay: float

        @return: 1 on success
        @rtype: integer
        """
        self._delaycmdexec = delay

    def launchapp(self, cmd, args = [], delay = 0, env = 1, lang = "C"):
        """
        Launch application.

        @param cmd: Command line string to execute.
        @type cmd: string
        @param args: Arguments to the application
        @type args: list
        @param delay: Delay after the application is launched
        @type delay: int
        @param env: GNOME accessibility environment to be set or not
        @type env: int
        @param lang: Application language to be used
        @type lang: string

        @return: PID of new process
        @rtype: integer

        @raise LdtpServerException: When command fails
        """
        os.environ['NO_GAIL'] = '0'
        os.environ['NO_AT_BRIDGE'] = '0'
        if env:
            os.environ['GTK_MODULES'] = 'gail:atk-bridge'
            os.environ['GNOME_ACCESSIBILITY'] = '1'
        if lang:
            os.environ['LANG'] = lang
        try:
            process = subprocess.Popen([cmd]+args, close_fds = True)
            # Let us wait so that the application launches
            try:
                time.sleep(int(delay))
            except ValueError:
                time.sleep(5)
        except Exception, e:
            raise LdtpServerException(str(e))
        os.environ['NO_GAIL'] = '1'
        os.environ['NO_AT_BRIDGE'] = '1'
        return process.pid

    def poll_events(self):
        """
        Poll for any registered events or window create events

        @return: window name
        @rtype: string
        """

        if not self._callback_event:
            return ''
        return self._callback_event.pop()

    def getlastlog(self):
        """
        Returns one line of log at any time, if any available, else empty string

        @return: log as string
        @rtype: string
        """

        if not self._custom_logger.log_events:
            return ''
        
        return self._custom_logger.log_events.pop()

    def startprocessmonitor(self, process_name, interval = 2):
        """
        Start memory and CPU monitoring, with the time interval between
        each process scan

        @param process_name: Process name, ex: firefox-bin.
        @type process_name: string
        @param interval: Time interval between each process scan
        @type interval: double

        @return: 1 on success
        @rtype: integer
        """
        if self._process_stats.has_key(process_name):
            # Stop previously running instance
            # At any point, only one process name can be tracked
            # If an instance already exist, then stop it
            self._process_stats[process_name].stop()
        # Create an instance of process stat
        self._process_stats[process_name] = ProcessStats(process_name, interval)
        # start monitoring the process
        self._process_stats[process_name].start()
        return 1

    def stopprocessmonitor(self, process_name):
        """
        Stop memory and CPU monitoring

        @param process_name: Process name, ex: firefox-bin.
        @type process_name: string

        @return: 1 on success
        @rtype: integer
        """
        if self._process_stats.has_key(process_name):
            # Stop monitoring process
            self._process_stats[process_name].stop()
        return 1

    def getcpustat(self, process_name):
        """
        get CPU stat for the give process name

        @param process_name: Process name, ex: firefox-bin.
        @type process_name: string

        @return: cpu stat list on success, else empty list
                If same process name, running multiple instance,
                get the stat of all the process CPU usage
        @rtype: list
        """
        # Create an instance of process stat
        _stat_inst = ProcessStats(process_name)
        _stat_list = []
        for i, procname in _stat_inst.get_cpu_memory_stat():
            # CPU percent returned with 14 decimal values
            # ex: 0.0281199122531, round it to 2 decimal values
            # as 0.03
            _stat_list.append(round(i['cpu_percent'], 2))
        return _stat_list

    def getmemorystat(self, process_name):
        """
        get memory stat

        @param process_name: Process name, ex: firefox-bin.
        @type process_name: string

        @return: memory stat list on success, else empty list
                If same process name, running multiple instance,
                get the stat of all the process memory usage
        @rtype: list
        """
        # Create an instance of process stat
        _stat_inst = ProcessStats(process_name)
        _stat_list = []
        for i, procname in _stat_inst.get_cpu_memory_stat():
            # Resident memory will be in bytes, to convert it to MB
            # divide it by 1024*1024
            _stat_list.append(i['proc_resident'] / (1024*1024))
        return _stat_list

    def windowuptime(self, window_name):
        """
        Get window uptime

        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 'starttime - endtime' in string format
        ex: '2010 01 12 14 21 13 - 2010 01 12 14 23 05'
        @rtype: string
        """

        if window_name in self._window_uptime and \
                len(self._window_uptime[window_name]) == 3:
            return '%s-%s' % (self._window_uptime[window_name][1],
                                self._window_uptime[window_name][2])
        for window in self._window_uptime:
            if re.match(glob_trans(window_name), window,
                        re.M | re.U | re.L) or \
                        re.match(glob_trans(window_name),
                                 self._window_uptime[window][0],
                                 re.M | re.U | re.L):
                        return '%s-%s' % (self._window_uptime[window][1],
                                          self._window_uptime[window][2])
        return ''

    def onwindowcreate(self, window_name):
        """
        Raise event on window create

        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1 if registration was successful, 0 if not.
        @rtype: integer
        """

        self._callback[window_name] = window_name

        return 1

    def removecallback(self, window_name):
        """
        Remove callback of window create

        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1 if remove was successful, 0 if not.
        @rtype: integer
        """

        if window_name in self._callback:
            del self._callback[window_name]

        return 1

    def registerevent(self, event_name):
        """
        Register at-spi event

        @param event_name: Event name in at-spi format.
        @type event_name: string

        @return: 1 if registration was successful, 0 if not.
        @rtype: integer
        """

        pyatspi.Registry.deregisterEventListener( \
            self._registered_event_cb, *self._registered_events)
        self._registered_events.append(event_name)
        pyatspi.Registry.registerEventListener(self._registered_event_cb,
                                               *self._registered_events)
        return 1

    def deregisterevent(self, event_name):
        """
        Remove callback of registered event

        @param event_name: Event name in at-spi format.
        @type event_name: string

        @return: 1 if remove was successful, 0 if not.
        @rtype: integer
        """

        for event in self._registered_events:
            if event_name == event:
                pyatspi.Registry.deregisterEventListener( \
                    self._registered_event_cb, *self._registered_events)
                self._registered_events.remove(event)
                pyatspi.Registry.registerEventListener( \
                    self._registered_event_cb, *self._registered_events)
                break
        return 1

    def registerkbevent(self, keys, modifiers = 0):
        """
        Register keyboard event

        @param keys: Key board entries
        @type keys: string
        @param modifiers: GTK based modifiers
        @type modifiers: int

        @return: 1 if registration was successful, 0 if not.
        @rtype: integer
        """

        key_op = KeyboardOp()
        key_vals = key_op.get_keyval_id(keys)
        if modifiers:
            self._kb_modifiers.append(modifiers)
        for key_val in key_vals:
            self._kb_entries.append(key_val.value)
        masks = [mask for mask in pyatspi.allModifiers()]
        pyatspi.Registry.registerKeystrokeListener(self._registered_kb_event_cb,
                                                   mask = masks,
                                                   kind=(pyatspi.KEY_PRESSED_EVENT,))
        return 1

    def deregisterkbevent(self, keys, modifiers = 0):
        """
        Remove callback of registered keyboard event

        @param keys: Key board entries
        @type keys: string
        @param modifiers: GTK based modifiers
        @type modifiers: int

        @return: 1 if remove was successful, 0 if not.
        @rtype: integer
        """

        key_op = KeyboardOp()
        key_vals = key_op.get_keyval_id(keys)
        if modifiers in self._kb_modifiers:
            del self._kb_modifiers[self._kb_modifiers.index(modifiers)]
        for key_val in key_vals:
            if key_val.value in self._kb_entries:
                del self._kb_entries[self._kb_entries.index(key_val.value)]
        masks = [mask for mask in pyatspi.allModifiers()]
        pyatspi.Registry.deregisterKeystrokeListener(self._registered_kb_event_cb,
                                                     mask = masks,
                                                     kind=(pyatspi.KEY_PRESSED_EVENT,))
        return 1

    def objectexist(self, window_name, object_name):
        """
        Checks whether a window or component exists.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type object_name: string

        @return: 1 if GUI was found, 0 if not.
        @rtype: integer
        """
        return self.guiexist(window_name, object_name)

    def maximizewindow(self, window_name = None):
        """
        Maximize a window using wnck
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1 if window maximized, 0 if not.
        @rtype: integer
        """
        if not wnckModule:
          raise LdtpServerException('Install python wnck module')
        waiter = MaximizeWindow(window_name)

        return int(waiter.run())

    def minimizewindow(self, window_name = None):
        """
        Minimize a window using wnck
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1 if window minimized, 0 if not.
        @rtype: integer
        """
        if not wnckModule:
          raise LdtpServerException('Install python wnck module')
        waiter = MinimizeWindow(window_name)

        return int(waiter.run())

    def unmaximizewindow(self, window_name = None):
        """
        Unmaximize a window using wnck
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1 if window unmaximized, 0 if not.
        @rtype: integer
        """
        if not wnckModule:
          raise LdtpServerException('Install python wnck module')
        waiter = UnmaximizeWindow(window_name)

        return int(waiter.run())

    def unminimizewindow(self, window_name = None):
        """
        Unminimize a window using wnck
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1 if window unminimized, 0 if not.
        @rtype: integer
        """
        if not wnckModule:
          raise LdtpServerException('Install python wnck module')
        waiter = UnminimizeWindow(window_name)

        return int(waiter.run())

    def activatewindow(self, window_name):
        """
        Activate a window using wnck
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1 if window unminimized, 0 if not.
        @rtype: integer
        """
        if not wnckModule:
          raise LdtpServerException('Install python wnck module')
        waiter = ActivateWindow(window_name)

        return int(waiter.run())

    def closewindow(self, window_name = None):
        """
        Close a window using wnck
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1 if window unminimized, 0 if not.
        @rtype: integer
        """
        if not wnckModule:
          raise LdtpServerException('Install python wnck module')
        waiter = CloseWindow(window_name)

        return int(waiter.run())

    def guiexist(self, window_name, object_name=''):
        """
        Checks whether a window or component exists.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type object_name: string

        @return: 1 if GUI was found, 0 if not.
        @rtype: integer
        """
        if object_name:
            waiter = ObjectExistsWaiter(window_name, object_name, 0)
        else:
            waiter = GuiExistsWaiter(window_name, 0)

        return int(waiter.run())

    def waittillguiexist(self, window_name, object_name = '',
                         guiTimeOut = 30, state = ''):
        """
        Wait till a window or component exists.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type object_name: string
        @param guiTimeOut: Wait timeout in seconds
        @type guiTimeOut: integer
        @param state: Object state used only when object_name is provided.
        @type object_name: string

        @return: 1 if GUI was found, 0 if not.
        @rtype: integer
        """
        if object_name:
            waiter = ObjectExistsWaiter(window_name, object_name, guiTimeOut, state)
        else:
            waiter = GuiExistsWaiter(window_name, guiTimeOut)

        return int(waiter.run())

    def waittillguinotexist(self, window_name, object_name = '', guiTimeOut = 30):
        """
        Wait till a window does not exist.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type object_name: string
        @param guiTimeOut: Wait timeout in seconds
        @type guiTimeOut: integer

        @return: 1 if GUI has gone away, 0 if not.
        @rtype: integer
        """
        if object_name:
            waiter = \
                ObjectNotExistsWaiter(window_name, object_name, guiTimeOut)
        else:
            waiter = GuiNotExistsWaiter(window_name, guiTimeOut)

        return int(waiter.run())

    def getobjectsize(self, window_name, object_name):
        """
        Get object size
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: x, y, width, height on success.
        @rtype: list
        """
        obj = self._get_object(window_name, object_name)

        _coordinates = self._get_size(obj)
        return [_coordinates.x, _coordinates.y, \
                    _coordinates.width, _coordinates.height]

    def getallstates(self, window_name, object_name):
        """
        Get all states of given object
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: list of string on success.
        @rtype: list
        """
        if re.search(';', object_name):
            obj = self._get_menu_hierarchy(window_name, object_name)
        else:
            obj = self._get_object(window_name, object_name)

        _state = obj.getState()
        _current_state = _state.getStates()
        _obj_states = []
        for state in _current_state:
            if self._state_names[state.real] == '':
               val = self._old_state_names[state]
            else:
               val = self._state_names[state]
            _obj_states.append(val)
        return _obj_states

    def hasstate(self, window_name, object_name, state, guiTimeOut = 0):
        """
        has state
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param guiTimeOut: Wait timeout in seconds
        @type guiTimeOut: integer

        @return: 1 on success.
        @rtype: integer
        """
        try:
            waiter = \
                ObjectExistsWaiter(window_name, object_name, guiTimeOut, state)
            return int(waiter.run())
        except:
          if self._ldtp_debug:
            print traceback.format_exc()
        return 0

    def grabfocus(self, window_name, object_name):
        """
        Grab focus.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        return 1

    def click(self, window_name, object_name):
        """
        Click item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        if obj.getRole() == pyatspi.ROLE_TOGGLE_BUTTON:
            self._click_object(obj, '(click|activate)')
        elif obj.getRole() == pyatspi.ROLE_COMBO_BOX:
            self._click_object(obj, '(click|press)')
        else:
            self._click_object(obj)

        return 1
    
    def press(self, window_name, object_name):
        """
        Press item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        self._click_object(obj, 'press')

        return 1
    
    def check(self, window_name, object_name):
        """
        Check item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        if self._check_state(obj, pyatspi.STATE_CHECKED) == False:
            self._click_object(obj, '(click|press|activate|check)')

        return 1

    def uncheck(self, window_name, object_name):
        """
        Uncheck item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)
        self._grab_focus(obj)

        if self._check_state(obj, pyatspi.STATE_CHECKED):
            self._click_object(obj, '(click|press|activate|uncheck)')

        return 1
    
    def verifytoggled(self, window_name, object_name):
        """
        Verify toggle item toggled.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        """
        return self.verifycheck(window_name, object_name)

    def verifypushbutton(self, window_name, object_name):
        """
        Verify whether the object is push button or not.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        """
        try:
            obj = self._get_object(window_name, object_name)

            return int(obj.getRole() == pyatspi.ROLE_PUSH_BUTTON)
        except:
            return 0

    def verifycheck(self, window_name, object_name):
        """
        Verify check item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        """
        try:
            obj = self._get_object(window_name, object_name)

            return int(self._check_state(obj, pyatspi.STATE_CHECKED))
        except:
            return 0

    def getpanelchildcount(self, window_name, object_name):
        """
        Get panel child count.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success, -1 on failure.
        @rtype: integer
        """
        try:
            obj = self._get_object(window_name, object_name)

            return obj.childCount
        except:
            return -1

    def selectpanel(self, window_name, object_name, index):
        """
        Select panel based on index.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param index: Index in panel to be selected. 
        @type index: integer

        @return: 1 on success, exception on failure.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)

        if obj.childCount <= 0:
          raise LdtpServerException("Panel doesn't have any children")
        elif index > obj.childCount or index < 0:
          raise LdtpServerException("Invalid index range")
        child = obj.getChildAtIndex(index)
        if not child:
          raise LdtpServerException("Unable to get child at index")
        self._grab_focus(child)
        return 1

    def selectpanelname(self, window_name, object_name, name):
        """
        Select panel based on name.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param name: name in panel to be selected. 
        @type name: string

        @return: 1 on success, exception on failure.
        @rtype: integer
        """
        obj = self._get_object(window_name, object_name)

        if obj.childCount <= 0:
          raise LdtpServerException("Panel doesn't have any children")
        for i in range(obj.childCount):
          child = obj.getChildAtIndex(i)
          if not child:
            continue
          if self._glob_match(name, child.name):
            self._grab_focus(child)
            return 1
        raise LdtpServerException("Unable to select panel child based on name")

    def verifyuncheck(self, window_name, object_name):
        """
        Verify uncheck item.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        """
        try:
            obj = self._get_object(window_name, object_name)

            return int(not self._check_state(obj, pyatspi.STATE_CHECKED))
        except:
            return 0

    def stateenabled(self, window_name, object_name):
        """
        Check whether an object state is enabled or not
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success 0 on failure.
        @rtype: integer
        """
        try:
            obj = self._get_object(window_name, object_name)

            return int(self._check_state(obj, pyatspi.STATE_ENABLED))
        except:
            return 0

    def getobjectlist(self, window_name):
        """
        Get list of items in given GUI.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: list of items in LDTP naming convention.
        @rtype: list
        """
        obj_list = []
        gui, _window_name = self._get_window_handle(window_name)
        if not gui:
            raise LdtpServerException('Unable to find window "%s"' % \
                                          window_name)

        for name in self._appmap_pairs(gui, _window_name).keys():
            obj_list.append(name)
        return obj_list

    def getobjectinfo(self, window_name, object_name):
        """
        Get object properties.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: list of properties
        @rtype: list
        """
        _window_handle, _window_name = \
            self._get_window_handle(window_name)
        if not _window_handle:
            raise LdtpServerException('Unable to find window "%s"' % \
                                          window_name)
        appmap = self._appmap_pairs(_window_handle, _window_name)

        obj_info = self._get_object_in_window(appmap, object_name)
        props = []
        if obj_info:
            for obj_prop in obj_info.keys():
                if obj_info[obj_prop]:
                    props.append(obj_prop)
        return props

    def getobjectproperty(self, window_name, object_name, prop):
        """
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
        """
        _window_handle, _window_name = \
            self._get_window_handle(window_name)
        if not _window_handle:
            raise LdtpServerException('Unable to find window "%s"' % \
                                          window_name)
        appmap = self._appmap_pairs(_window_handle, _window_name)

        obj_info = self._get_object_in_window(appmap, object_name)
        if obj_info and prop in obj_info:
            return obj_info[prop]
        raise LdtpServerException('Unknown property "%s" in %s' % \
                                      (prop, object_name))

    def getchild(self, window_name, child_name = '', role = '', parent = ''):
        """
        Gets the list of object available in the window, which matches 
        component name or role name or both.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param child_name: Child name to search for.
        @type child_name: string
        @param role: role name to search for, or an empty string for wildcard.
        @type role: string
        @param parent: parent name to search for, or an empty string for wildcard.
        @type role: string

        @return: list of matched children names
        @rtype: list
        """
        matches = []
        if role:
            role = re.sub(' ', '_', role)
        if parent and (child_name or role):
            _window_handle, _window_name = \
                self._get_window_handle(window_name)
            if not _window_handle:
                raise LdtpServerException('Unable to find window "%s"' % \
                                              window_name)
            appmap = self._appmap_pairs(_window_handle, _window_name)
            obj = self._get_object_in_window(appmap, parent)
            obj_name = appmap[obj['key']]
            def _get_all_children_under_obj(obj, child_list):
                if role and obj['class'] == role:
                    child_list.append(obj['key'])
                elif child_name and self._match_name_to_appmap(child_name, obj):
                    child_list.append(obj['key'])
                if obj:
                    children = obj['children']
                if not children:
                    return child_list
                for child in children:
                    return _get_all_children_under_obj( \
                        appmap[child],
                        child_list)

            matches = _get_all_children_under_obj(obj, [])
            if not matches:
                if child_name:
                    _name = 'name "%s" ' % child_name
                if role:
                    _role = 'role "%s" ' % role
                if parent:
                    _parent = 'parent "%s"' % parent
                exception = 'Could not find a child %s%s%s' % (_name, _role, _parent)
                raise LdtpServerException(exception)

            return matches

        _window_handle, _window_name = \
            self._get_window_handle(window_name)
        if not _window_handle:
            raise LdtpServerException('Unable to find window "%s"' % \
                                          window_name)
        appmap = self._appmap_pairs(_window_handle, _window_name)
        for name in appmap.keys():
            obj = appmap[name]
            # When only role arg is passed
            if role and not child_name and obj['class'] == role:
                matches.append(name)
            # When parent and child_name arg is passed
            if parent and child_name and not role and \
                    self._match_name_to_appmap(parent, obj):
                matches.append(name)
            # When only child_name arg is passed
            if child_name and not role and \
                    self._match_name_to_appmap(child_name, obj):
                matches.append(name)
            # When role and child_name args are passed
            if role and child_name and obj['class'] == role and \
                    self._match_name_to_appmap(child_name, obj):
                matches.append(name)

        if not matches:
            _name = ''
            _role = ''
            _parent = ''
            if child_name:
                _name = 'name "%s" ' % child_name
            if role:
                _role = 'role "%s" ' % role
            if parent:
                _parent = 'parent "%s"' % parent
            exception = 'Could not find a child %s%s%s' % (_name, _role, _parent)
            raise LdtpServerException(exception)

        return matches

    def remap(self, window_name):
        """
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string

        @return: 1
        @rtype: integer
        """
        _window_handle, _window_name = \
            self._get_window_handle(window_name)
        if not _window_handle:
            raise LdtpServerException('Unable to find window "%s"' % \
                                          window_name)
        self._appmap_pairs(_window_handle, _window_name, True)
        return 1

    def wait(self, timeout=5):
        """
        Wait a given amount of seconds.

        @param timeout: Wait timeout in seconds
        @type timeout: double

        @return: 1
        @rtype: integer
        """
        if timeout < 1:
            # If timeout < 1, like 0.5 then use
            # time.sleep, using > 1 its not recommended to use
            # this, as it hangs the desktop for the sleep time
            time.sleep(timeout)
            return 1
        waiter = NullWaiter(1, timeout)
        return waiter.run()

    def getstatusbartext(self, window_name, object_name):
        """
        Get text value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: text on success.
        @rtype: string
        """
        return self.gettextvalue(window_name, object_name)

    def setlocale(self, locale_str):
        """
        Set the locale to the given value.

        @param locale_str: locale to set to.
        @type locale_str: string

        @return: 1
        @rtype: integer
        """
        locale.setlocale(locale.LC_ALL, locale_str)
        return 1

    def getwindowsize(self, window_name):
        """
        Get window size.
        
        @param window_name: Window name to get size of.
        @type window_name: string

        @return: list of dimensions [x, y, w, h]
        @rtype: list
        """
        for gui in self._list_guis():
            if self._match_name_to_acc(window_name, gui):
                size = self._get_size(gui)
                return [size.x, size.y, size.width, size.height]

        raise LdtpServerException(u'Window "%s" does not exist' % window_name)

    def _getComponentAtCoords(self, parent, x, y):
        """
        Gets any child accessible that resides under given desktop coordinates.

        @param parent: Top-level accessible.
        @type parent: L{Accessibility.Accessible}
        @param x: X coordinate.
        @type x: integer
        @param y: Y coordinate.
        @type y: integer

        @return: Child accessible at given coordinates, or None.
        @rtype: L{Accessibility.Accessible}
        """
        # Following lines from Accerciser, _getComponentAtCoords method
        # quick_select.py file
        container = parent
        inner_container = parent
        while True:
            container_role = container.getRole()
            if container_role == pyatspi.ROLE_PAGE_TAB_LIST:
                try:
                    si = container.querySelection()
                    container = si.getSelectedChild(0)[0]
                except NotImplementedError:
                    pass
            try:
                ci = container.queryComponent()
            except:
                break
            else:
                inner_container = container
            container =  ci.getAccessibleAtPoint(x, y, pyatspi.DESKTOP_COORDS)
            if not container or container.queryComponent() == ci:
                # The gecko bridge simply has getAccessibleAtPoint return itself
                # if there are no further children
                break
        if inner_container == parent:
            return None
        else:
            return inner_container

    def getobjectnameatcoords(self, wait_time = 0.0):
        """
        Get object name at coordinates

        @param timeout: Wait timeout in seconds
        @type timeout: double

        
        @return: window name as string and all possible object names
                matching name and type as list of string [objectname]
        @rtype: (string, list)
        """
        if not wnckModule:
          raise LdtpServerException('Install python wnck module')
        self.wait(wait_time)
        # Following lines from Accerciser, _inspectUnderMouse method
        # quick_select.py file
        # Inspect accessible under mouse
        if gtk3:
           display = gdk.get_default_root_window()
           screen, x, y, flags = display.get_pointer()
        else:
           display = gtk.gdk.Display(gtk.gdk.get_display())
           screen, x, y, flags = display.get_pointer()
           del screen # A workaround http://bugzilla.gnome.org/show_bug.cgi?id=593732
        # Bug in wnck, if the following 2 lines are not called
        # wnck returns empty list
        while gtk.events_pending():
            gtk.main_iteration()
        if gtk3:
          wnck_screen = wnck.Screen.get_default()
        else:
          wnck_screen = wnck.screen_get_default()
        wnck_screen.force_update()

        window_order = [(w.get_name(), w) \
                        for w in wnck_screen.get_windows_stacked()]
        tmp_window_order = []
        for w in window_order:
            if w[0] != 'Untitled window':
                # If not 'Untitled window', just assign it directly to
                # tmp_window_order
                tmp_window_order.append(w)
                continue
            # Get PID
            pid = w[1].get_pid()
            if not pid:
                # PID not found
                continue
            # Get process name
            ps = subprocess.Popen('ps ch -o %%c %d' % pid, shell=True,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE)
            stdout, stderr = ps.communicate()
            # Strip \n
            stdout = re.sub('\n', '', stdout)
            # Get child_windows of current application
            child_windows = [child_window.get_name() for child_window in \
                             w[1].get_application().get_windows()]
            for app in self._list_apps():
                if not app[0]:
                    continue
                if stdout != app[0].name:
                    continue
                # if stdout == app[0].name:
                for gui in app[0]:
                    if not gui: continue
                    # If current a11y gui.name doesn't match the
                    # Wnck window names, let us assume, its the window
                    # name, replace 'Untitled window' with gui.name
                    if gui.name not in child_windows:
                        # Direct tuple assignment is not possible
                        # and so assigning in tmp tuple list
                        tmp_window_order.append((gui.name, w[1]))
                        # Let us assume, just only one window
                        # with 'Untitled window'
                        break

        # Assign back tmp_window_order to window_order, after all the iteration
        window_order = tmp_window_order

        top_window = (None, -1)
        z_order = -1
        for gui in self._list_guis():
            acc = self._getComponentAtCoords(gui, x, y)
            if acc:
                try:
                    for w in window_order:
                        if gui.name == w[0]:
                            # wnck returns empty window name as "Untitled window"
                            # also gui.name doesn't match wnck window name in some cases
                            # eg: Gedit Question dialog, when you try to close
                            # unsaved document
                            z_order = window_order.index(w)
                            break
                except ValueError:
                    # It's possibly a popup menu, so it would not be in our frame name
                    # list. And if it is, it is probably the top-most component.
                    try:
                        if acc.queryComponent().getLayer() == pyatspi.LAYER_POPUP:
                            return (None, None)
                    except:
                        pass
                else:
                    if z_order > top_window[1]:
                        top_window = (acc, z_order)
        if top_window[0]:
            # top_window[1] holds the window name and Wnck window info
            # [0] holds the window name
            window_name = window_order[top_window[1]][0]
            child_object = top_window[0]
            child_list = self.getchild(window_name, child_object.name,
                                       child_object.getRoleName())
            if len(child_list) > 1:
                # If child list is more than 1 child, then
                # return the list to the caller
                possible_child = child_list
            else:
                # else, just return the only element
                possible_child = child_list[0]
            # NOTE: Bug, when a window title is empty
            # the accessibility window in the list matching the
            # x, y coordinates is returned !
            return (self._get_window_handle(window_name)[1], possible_child)
        return (None, None)
