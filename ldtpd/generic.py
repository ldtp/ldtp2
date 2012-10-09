"""
LDTP v2 Core Generic.

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

import gc
import os
try:
  # If we have gtk3+ gobject introspection, use that
  from gi.repository import Gtk as gtk, Gdk as gdk
  gtk3 = True
except:
  # No gobject introspection, use gtk2
  import gtk
  gtk3 = False
import pyatspi 
import tempfile
from base64 import b64encode

from utils import Utils
from server_exception import LdtpServerException

class Generic(Utils):
    def imagecapture(self, window_name = None, x = 0, y = 0,
                     width = None, height = None):
        """
        Captures screenshot of the whole desktop or given window
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param x: x co-ordinate value
        @type x: int
        @param y: y co-ordinate value
        @type y: int
        @param width: width co-ordinate value
        @type width: int
        @param height: height co-ordinate value
        @type height: int

        @return: screenshot with base64 encoded for the client
        @rtype: string
        """	
        # Validate the parameters
        # x and y offsets cannot be nagative
        x = max(0, x)
        y = max(0, y)

        # height and width cannot be less than 1
        # set to None if nagative value is given
        if width < 1:
            width = None
        if height < 1:
            height = None
	
        if window_name:
            acc = None
            for gui in self._list_guis():
                if self._match_name_to_acc(window_name, gui):
                    if 'Component' in pyatspi.listInterfaces(gui):
                        acc = gui
                        for obj in self._list_objects(gui):
                            role = obj.getRole()
                            if role == pyatspi.ROLE_CHECK_BOX or \
                                    role == pyatspi.ROLE_PUSH_BUTTON or \
                                    role == pyatspi.ROLE_RADIO_BUTTON:
                                try:
                                    # Try to grab focus
                                    self._grab_focus(obj)
                                except:
                                    pass
                                # Inner for loop
                                break
                        # Outer for loop
                        break
            if not acc:
                raise LdtpServerException('No window matches %s' % window_name)
            icomponent = acc.queryComponent()
            bb = icomponent.getExtents(pyatspi.DESKTOP_COORDS)
            # If co-ordinates are provided, use it
            # offsets cannot be greater than or equal to the window size
            # we want to capture at least one pixel
            x = min(x, bb.width - 1)
            y = min(y, bb.height - 1)

            # adjust the width and height parameters
            # so that the captured image is contained
            # within the visible window area
            # Take into account that window may be only
            # partially on the screen then the reported
            # width and height are not the same as the area of the window
            # that can actually be captured.
            
            # if bb.x is negative then the actual width 
            # is smaller than the bb.width
            leftClippedWidth = min(bb.width, bb.width + bb.x)
            
            # if bb.y is negative then the actual height
            # is smaller than the bb.height
            topClippedHeight = min(bb.height, bb.height + bb.y)
            
            # Clipping from the right and bottom is done later
            # when the desktop size is known            
            if width == None:                
                width = leftClippedWidth - x
            else:
                width = min(width, leftClippedWidth - x)
            if height == None:
                height = topClippedHeight - y
            else:
                height = min(height, topClippedHeight - y)

            # take the window position into account
            # use 0 as the window co-oridinate
            # if it is negative
            x = x + max(0, bb.x)
            y = y + max(0, bb.y)

        tmpFile = tempfile.mktemp('.png', 'ldtpd_')
        if gtk3:
           window = gdk.get_default_root_window()
           tmp_size = window.get_geometry()
           size = []
           # Width
           size.append(tmp_size[2])
           # Height
           size.append(tmp_size[3])
           # offsets cannot be greater than or equal to the desktop size
           # we want to capture at least one pixel
           x = min(x, size[0] - 1)
           y = min(y, size[1] - 1)
	   
           # adjust the width and height parameters
           # so that the captured image is contained
           # within the desktop area
           if width == None:
               width = size[0] - x
           else:
               width = min(width, size[0] - x)
           if height == None:
               height = size[1] - y
           else:
               height = min(height, size[1] - y)
           pb = gdk.pixbuf_get_from_window(window, x, y, width,
                                           height)
           pb.savev(tmpFile, 'png', [], [])
           del pb
           gc.collect()
        else:
           window = gtk.gdk.get_default_root_window()
           size = window.get_size()
           # offsets cannot be greater than or equal to the desktop size
           # we want to capture at least one pixel
           x = min(x, size[0] - 1)
           y = min(y, size[1] - 1)
	   
           # adjust the width and height parameters
           # so that the captured image is contained
           # within the desktop area
           if width == None:
               width = size[0] - x
           else:
               width = min(width, size[0] - x)
           if height == None:
               height = size[1] - y
           else:
               height = min(height, size[1] - y)
           pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 
                               width, 
                               height)
           pb = pb.get_from_drawable(window, window.get_colormap(),
                                      x, y, 0, 0, 
                                      width, 
                                      height)

           if pb:
              pb.save(tmpFile, 'png')
              del pb
              gc.collect()
        rv = b64encode(open(tmpFile).read())
        os.remove(tmpFile)
        return rv

