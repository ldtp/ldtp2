'''
LDTP v2 Mouse.

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

class Mouse(Utils):
    '''
    Mouse related events
    '''
    def generatemouseevent(self, x, y, eventType = 'b1c'):
        '''
        Generate mouse event on x, y co-ordinates.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: int
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: int

        @return: 1 on success.
        @rtype: integer
        '''
        return self._mouse_event(x, y, eventType)

    def mouseleftclick(self, window_name, object_name):
        '''
        Mouse left click on an object.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        self._grab_focus(obj)

        _coordinates = self._get_size(obj)
        return self._mouse_event(_coordinates.x + _coordinates.width / 2,
                                 _coordinates.y + _coordinates.height / 2,
                                 'b1c')

    def mousemove(self, window_name, object_name):
        '''
        Mouse move on an object.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        self._grab_focus(obj)

        _coordinates = self._get_size(obj)
        return self._mouse_event(_coordinates.x + _coordinates.width / 2,
                                 _coordinates.y + _coordinates.height / 2,
                                 'abs')

    def mouserightclick(self, window_name, object_name):
        '''
        Mouse right click on an object.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        self._grab_focus(obj)

        _coordinates = self._get_size(obj)
        return self._mouse_event(_coordinates.x + _coordinates.width / 2,
                                 _coordinates.y + _coordinates.height / 2,
                                 'b3c')

    def doubleclick(self, window_name, object_name):
        '''
        Double click on the object
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        self._grab_focus(obj)

        _coordinates = self._get_size(obj)
        return self._mouse_event(_coordinates.x + _coordinates.width / 2,
                                 _coordinates.y + _coordinates.height / 2,
                                 'b1d')
