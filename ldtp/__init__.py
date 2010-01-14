'''
LDTP v2 client init file

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

import os
import re
import time
import state
import client
import atexit
import thread
import gobject
import datetime
import tempfile
import traceback
from base64 import b64decode
from fnmatch import translate as glob_trans
from client_exception import LdtpExecutionError

_pollEvents = None

def setHost(host):
    client._client.setHost(host)

def whoismyhost():
    return client._client._ServerProxy__host

def log(self, *args):
    # Do nothing. For backward compatability
    pass

def _populateNamespace(d):
    for method in client._client.system.listMethods():
        if method.startswith('system.'):
            continue
        if d.has_key(method):
            local_name = '_remote_' + method
        else:
            local_name = method
        d[local_name] = getattr(client._client, method)
        d[local_name].__doc__ = client._client.system.methodHelp(method)

class PollEvents:
    def __init__(self):
        self._stop = False
        self._callback = {}

    def __del__(self):
        self._stop = True

    def run(self):
        while not self._stop:
            status = self.poll_server()
            if status is False:
                # Socket error
                break
            elif status is None:
                # No event in queue, sleep a second
                time.sleep(1)

    def poll_server(self):
        if not self._callback:
            return
        try:
            event = poll_events()
        except socket.error:
            return False

        if not event:
            return None

        # Event format:
        # window:create-Untitled Document 1 - gedit
        event = event.split('-', 1) # Split first -
        window_name = event[1]
        event = event[0] # Just event type
        # self._callback[window][0] - Event type
        # self._callback[window][1] - Callback function
        # self._callback[window][2] - Arguments to callback function
        for window in self._callback:
            if (event == "onwindowcreate" and \
                    re.match(glob_trans(window),
                             window_name, re.M | re.U | re.L)) or \
                             (event != "onwindowcreate" and \
                                  self._callback[window][0] == event):
                             callback = self._callback[window][1]
                             if callable(callback):
                                 try:
                                     args = self._callback[window][2]
                                     if len(args) and args[0]:
                                         # If one or more args
                                         thread.start_new_thread(callback, args)
                                     else:
                                         # No args to the callback function
                                         thread.start_new_thread(callback, ())
                                         #callback()
                                 except:
                                     pass
        return True

def imagecapture(window_name = None, out_file = None, x = 0, y = 0,
                 width = None, height = None):
    '''
    Captures screenshot of the whole desktop or given window

    @param window_name: Window name to look for, either full name,
    LDTP's name convention, or a Unix glob.
    @type window_name: string
    @param x: x co-ordinate value
    @type x: integer
    @param y: y co-ordinate value
    @type y: integer
    @param width: width co-ordinate value
    @type width: integer
    @param height: height co-ordinate value
    @type height: integer

    @return: screenshot filename
    @rtype: string
    '''
    if not out_file:
        out_file = tempfile.mktemp('.png', 'ldtp_')
    else:
        out_file = os.path.expanduser(out_file)
        
    data = _remote_imagecapture(window_name, x, y, width, height)
    f = open(out_file, 'w')
    f.write(b64decode(data))
    f.close()

    return out_file

def onwindowcreate(window_name, fn_name, *args):
    '''
    On window create, call the function with given arguments

    @param window_name: Window name to look for, either full name,
    LDTP's name convention, or a Unix glob.
    @type window_name: string
    @param fn_name: Callback function
    @type fn_name: function
    @param *args: arguments to be passed to the callback function
    @type *args: var args

    @return: 1 if registration was successful, 0 if not.
    @rtype: integer
    '''

    _pollEvents._callback[window_name] = ["onwindowcreate", fn_name, args]
    return _remote_onwindowcreate(window_name)

def removecallback(window_name):
    '''
    Remove registered callback on window create

    @param window_name: Window name to look for, either full name,
    LDTP's name convention, or a Unix glob.
    @type window_name: string

    @return: 1 if registration was successful, 0 if not.
    @rtype: integer
    '''

    if window_name in _pollEvents._callback:
        del _pollEvents._callback[window_name]
    return _remote_removecallback(window_name)

def registerevent(event_name, fn_name, *args):
    '''
    Register at-spi event

    @param event_name: Event name in at-spi format.
    @type event_name: string
    @param fn_name: Callback function
    @type fn_name: function
    @param *args: arguments to be passed to the callback function
    @type *args: var args

    @return: 1 if registration was successful, 0 if not.
    @rtype: integer
    '''

    _pollEvents._callback[event_name] = [event_name, fn_name, args]
    return _remote_registerevent(event_name)

def removeevent(event_name):
    '''
    Remove callback of registered event

    @param event_name: Event name in at-spi format.
    @type event_name: string

    @return: 1 if registration was successful, 0 if not.
    @rtype: integer
    '''

    if event_name in _pollEvents._callback:
        del _pollEvents._callback[event_name]
    return _remote_removeevent(event_name)

def windowuptime(window_name):
    '''
    Get window uptime
    
    @param window_name: Window name to look for, either full name,
    LDTP's name convention, or a Unix glob.
    @type window_name: string

    @return: "starttime, endtime" as datetime python object
    '''

    tmp_time = _remote_windowuptime(window_name)
    if tmp_time:
        tmp_time = tmp_time.split('-')
        start_time = tmp_time[0].split(' ')
        end_time = tmp_time[1].split(' ')
        _start_time = datetime.datetime(int(start_time[0]), int(start_time[1]),
                                        int(start_time[2]), int(start_time[3]),
                                        int(start_time[4]), int(start_time[5]))
        _end_time = datetime.datetime(int(end_time[0]), int(end_time[1]),
                                      int(end_time[2]),int(end_time[3]),
                                      int(end_time[4]), int(end_time[5]))
        return _start_time, _end_time
    return None

_populateNamespace(globals())
_pollEvents = PollEvents()
thread.start_new_thread(_pollEvents.run, ())

atexit.register(client._client.kill_daemon)
