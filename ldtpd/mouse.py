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

    def simulatemousemove(self, source_x, source_y, dest_x, dest_y):
        """
        @param source_x: Source X
        @type source_x: integer
        @param source_y: Source Y
        @type source_y: integer
        @param dest_x: Dest X
        @type dest_x: integer
        @param dest_y: Dest Y
        @type dest_y: integer

        @return: 1 if simulation was successful, 0 if not.
        @rtype: integer
        """
        size = self._get_size(self._desktop)
        if (source_x < size.x or source_y < size.y or \
                dest_x > size.width or dest_y > size.height) and \
                (source_x > size.width or source_y > size.height or \
                     dest_x < size.x or dest_y < size.y):
            return 0

        x_flag = False # Iterated x ?
        y_flag = False # Iterated y ?
        while True:
            if not x_flag:
                if source_x > dest_x:
                    # If source X greather than dest X
                    # then move -1 pixel
                    source_x -= 1
                elif source_x < dest_x:
                    # If source X less than dest X
                    # then move +1 pixel
                    source_x += 1
                else:
                    # If source X equal to dest X
                    # then don't process X co-ordinate
                    x_flag = True
            if not y_flag:
                if source_y > dest_y:
                    # If source Y greather than dest Y
                    # then move -1 pixel
                    source_y -= 1
                elif source_y < dest_y:
                    # If source Y less than dest Y
                    # then move +1 pixel
                    source_y += 1
                else:
                    # If source Y equal to dest Y
                    # then don't process Y co-ordinate
                    y_flag = True
            # Start mouse move from source_x, source_y to dest_x, dest_y
            self.generatemouseevent(source_x, source_y, 'abs')
            if source_x == dest_x and source_y == dest_y:
                # If we have reached the dest_x and dest_y
                # then break the loop
                break
        return 1
