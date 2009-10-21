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
import gobject, pyatspi

_main_loop = gobject.MainLoop()

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
        _main_loop.run()
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
            _main_loop.quit()
            return False
        return True
    
    def poll(self):
        pass

    def _event_cb(self, event):
        self.event_cb(event)
        if self.success:
            _main_loop.quit()

    def event_cb(self, event):
        pass

class NullWaiter(Waiter):
    def __init__(self, return_value, timeout):
        self._return_value = return_value
        Waiter.__init__(self, timeout)

    def run(self):
        Waiter.run(self)
        return self._return_value

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
    def __init__(self, frame_name, obj_name, timeout):
        GuiExistsWaiter.__init__(self, frame_name, timeout)
        self._obj_name = obj_name

    def poll(self):
        try:
            if re.search(';', object_name):
                self._get_menu_hierarchy(self._frame_name, self._obj_name)
            else:
                self._get_object(self._frame_name, self._obj_name)
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
            if re.search(';', object_name):
                self._get_menu_hierarchy(self._frame_name, self._obj_name)
            else:
                self._get_object(self._frame_name, self._obj_name)
            self.success = False
        except:
            self.success = True

if __name__ == "__main__":
    waiter = ObjectExistsWaiter('frmCalculator', 'mnuEitanIsaacsonFoo', 0)
    print waiter.run()
