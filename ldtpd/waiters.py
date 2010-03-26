'''
LDTP v2 waiters.

@author: Eitan Isaacson <eitan@ascender.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See "COPYING" in the source distribution for more information.

Headers in this file shall remain intact.
'''

from utils import Utils
import re
import gtk
import time
import wnck
import fnmatch
import gobject
import pyatspi
import traceback

class Waiter(Utils):
    events = []
    def __init__(self, timeout):
        Utils.__init__(self)
        self.timeout = timeout

    def run(self):
        self.success = False
        self._timeout_count = 0

        try:
            self.poll()
        except:
            pass

        if self.success or self.timeout == 0:
            return self.success

        gobject.timeout_add_seconds(1, self._timeout_cb)
        if self.events:
            pyatspi.Registry.registerEventListener(
                self._event_cb, *self.events)
        gtk.main()
        if self.events:
            pyatspi.Registry.deregisterEventListener(
                self._event_cb, *self.events)
        return self.success

    def _timeout_cb(self):
        if self.success: # dispose of previous waiters.
            return False
        self._timeout_count += 1
        self.poll()
        if self._timeout_count >= self.timeout or self.success:
            gtk.main_quit()
            return False
        return True
    
    def poll(self):
        pass

    def _event_cb(self, event):
        self.event_cb(event)
        if self.success:
            gtk.main_quit()

    def event_cb(self, event):
        pass

class NullWaiter(Waiter):
    def __init__(self, return_value, timeout):
        self._return_value = return_value
        Waiter.__init__(self, timeout)

    def run(self):
        Waiter.run(self)
        return self._return_value

class MaximizeWindow(Waiter):
    def __init__(self, frame_name):
        Waiter.__init__(self, timeout = 0)
        self._frame_name = frame_name

    def poll(self):
        screen = wnck.screen_get_default()
        while gtk.events_pending():
            gtk.main_iteration()
        window_list = screen.get_windows()
        for w in window_list:
            if self._frame_name:
                current_window = w.get_name()
                if re.search(
                    fnmatch.translate(self._frame_name), current_window,
                    re.U | re.M | re.L) \
                    or re.search(fnmatch.translate(re.sub("(^frm)|(^dlg)", "",
                                                          self._frame_name)),
                                 re.sub(" *(\t*)|(\n*)", "", current_window),
                                 re.U | re.M | re.L):
                    # If window name specified, then maximize just that window
                    w.maximize()
                    self.success = True
                    break
            else:
                # Maximize all window
                w.maximize()
                self.success = True

class MinimizeWindow(Waiter):
    def __init__(self, frame_name):
        Waiter.__init__(self, timeout = 0)
        self._frame_name = frame_name

    def poll(self):
        screen = wnck.screen_get_default()
        while gtk.events_pending():
            gtk.main_iteration()
        window_list = screen.get_windows()
        for w in window_list:
            if self._frame_name:
                current_window = w.get_name()
                if re.search( \
                    fnmatch.translate(self._frame_name), current_window,
                    re.U | re.M | re.L) \
                    or re.search(fnmatch.translate(re.sub("(^frm)|(^dlg)", "",
                                                          self._frame_name)),
                                 re.sub(" *(\t*)|(\n*)", "", current_window),
                                 re.U | re.M | re.L):
                    # If window name specified, then minimize just that window
                    w.minimize()
                    self.success = True
                    break
            else:
                # Minimize all window
                w.minimize()
                self.success = True

class UnmaximizeWindow(Waiter):
    def __init__(self, frame_name):
        Waiter.__init__(self, timeout = 0)
        self._frame_name = frame_name

    def poll(self):
        screen = wnck.screen_get_default()
        while gtk.events_pending():
            gtk.main_iteration()
        window_list = screen.get_windows()
        for w in window_list:
            if self._frame_name:
                current_window = w.get_name()
                if re.search( \
                    fnmatch.translate(self._frame_name), current_window,
                    re.U | re.M | re.L) \
                    or re.search(fnmatch.translate(re.sub("(^frm)|(^dlg)", "",
                                                          self._frame_name)),
                                 re.sub(" *(\t*)|(\n*)", "", current_window),
                                 re.U | re.M | re.L):
                    # If window name specified, then unmaximize just that window
                    w.unmaximize()
                    self.success = True
                    break
            else:
                # Unmaximize all window
                w.unmaximize()
                self.success = True

class UnminimizeWindow(Waiter):
    def __init__(self, frame_name):
        Waiter.__init__(self, timeout = 0)
        self._frame_name = frame_name

    def poll(self):
        screen = wnck.screen_get_default()
        while gtk.events_pending():
            gtk.main_iteration()
        window_list = screen.get_windows()
        for w in window_list:
            if self._frame_name:
                current_window = w.get_name()
                if re.search( \
                    fnmatch.translate(self._frame_name), current_window,
                    re.U | re.M | re.L) \
                    or re.search(fnmatch.translate(re.sub("(^frm)|(^dlg)", "",
                                                          self._frame_name)),
                                 re.sub(" *(\t*)|(\n*)", "", current_window),
                                 re.U | re.M | re.L):
                    # If window name specified, then unminimize just that window
                    w.unminimize(int(time.time()))
                    self.success = True
                    break
            else:
                # Unminimize all window
                w.unminimize(int(time.time()))
                self.success = True

class ActivateWindow(Waiter):
    def __init__(self, frame_name):
        Waiter.__init__(self, timeout = 0)
        self._frame_name = frame_name

    def poll(self):
        screen = wnck.screen_get_default()
        while gtk.events_pending():
            gtk.main_iteration()
        window_list = screen.get_windows()
        for w in window_list:
            if self._frame_name:
                current_window = w.get_name()
                if re.search( \
                    fnmatch.translate(self._frame_name), current_window,
                    re.U | re.M | re.L) \
                    or re.search(fnmatch.translate(re.sub("(^frm)|(^dlg)", "",
                                                          self._frame_name)),
                                 re.sub(" *(\t*)|(\n*)", "", current_window),
                                 re.U | re.M | re.L):
                    # If window name specified, then activate just that window
                    w.activate(int(time.time()))
                    self.success = True
                    break
            else:
                break

class CloseWindow(Waiter):
    def __init__(self, frame_name):
        Waiter.__init__(self, timeout = 0)
        self._frame_name = frame_name

    def poll(self):
        screen = wnck.screen_get_default()
        while gtk.events_pending():
            gtk.main_iteration()
        window_list = screen.get_windows()
        for w in window_list:
            if self._frame_name:
                current_window = w.get_name()
                if re.search( \
                    fnmatch.translate(self._frame_name), current_window,
                    re.U | re.M | re.L) \
                    or re.search(fnmatch.translate(re.sub("(^frm)|(^dlg)", "",
                                                          self._frame_name)),
                                 re.sub(" *(\t*)|(\n*)", "", current_window),
                                 re.U | re.M | re.L):
                    # If window name specified, then close just that window
                    w.close(int(time.time()))
                    self.success = True
                    break
            else:
                # Close all window
                w.close(int(time.time()))
                self.success = True

class GuiExistsWaiter(Waiter):
    events = ["window:create"]
    def __init__(self, frame_name, timeout):
        Waiter.__init__(self, timeout)
        self._frame_name = frame_name
        self.top_level = None # Useful in subclasses

    def poll(self):
        gui = self._get_window_handle(self._frame_name)
        self.success = bool(gui)

    def event_cb(self, event):
        if self._match_name_to_acc(self._frame_name, event.source):
            self.top_level = event.source
            self.success = True

class GuiNotExistsWaiter(Waiter):
    events = ["window:destroy"]
    def __init__(self, frame_name, timeout):
        Waiter.__init__(self, timeout)
        self.top_level = None
        self._frame_name = frame_name

    def poll(self):
        gui = self._get_window_handle(self._frame_name)
        self.success = not bool(gui)

    def event_cb(self, event):
        if self._match_name_to_acc(self._frame_name, event.source):
            self.success = True

class ObjectExistsWaiter(GuiExistsWaiter):
    def __init__(self, frame_name, obj_name, timeout, state = ''):
        GuiExistsWaiter.__init__(self, frame_name, timeout)
        self._obj_name = obj_name
        self._state = state

    def poll(self):
        try:
            if re.search(';', self._obj_name):
                obj = self._get_menu_hierarchy(self._frame_name, self._obj_name)
            else:
                obj = self._get_object(self._frame_name, self._obj_name)
            if self._state:
                _state_inst = obj.getState()
                _obj_state = _state_inst.getStates()
                state = 'STATE_%s' % self._state.upper()
                if state in self._states and \
                        self._states[state] in _obj_state:
                    self.success = True
            else:
                self.success = True
        except:
            pass

    def event_cb(self, event):
        GuiExistsWaiter.event_cb(self, event)
        self.success = False

class ObjectNotExistsWaiter(GuiNotExistsWaiter):
    def __init__(self, frame_name, obj_name, timeout):
        GuiNotExistsWaiter.__init__(self, frame_name, timeout)
        self._obj_name = obj_name

    def poll(self):
        try:
            if re.search(';', self._obj_name):
                self._get_menu_hierarchy(self._frame_name, self._obj_name)
            else:
                self._get_object(self._frame_name, self._obj_name)
            self.success = False
        except:
            self.success = True

if __name__ == "__main__":
    waiter = ObjectExistsWaiter('frmCalculator', 'mnuEitanIsaacsonFoo', 0)
    print waiter.run()
