'''
LDTP v2 Core Generic.

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
import gc
import os
import gtk
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
            x, y, height, width = bb.x, bb.y, bb.height, bb.width

        window = gtk.gdk.get_default_root_window()
        size = window.get_size()
        pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 
                            width or size [0], 
                            height or size [1])
        pb = pb.get_from_drawable(window, window.get_colormap(),
                                   x, y, 0, 0, 
                                   width or size [0], 
                                   height or size [1])

        if pb:
            tmpFile = tempfile.mktemp('.png', 'ldtpd_')
            pb.save(tmpFile, 'png')
            del pb
            gc.collect()
        rv = b64encode(open(tmpFile).read())
        os.remove(tmpFile)
        return rv
