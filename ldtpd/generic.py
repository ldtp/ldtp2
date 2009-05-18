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
import pyatspi 
import tempfile
import gc
import gtk
import os
from base64 import b64encode

from utils import Utils
from server_exception import LdtpServerException

class Generic(Utils):
    def imagecapture(self, winName = None, resolution1 = None,
                     resolution2 = None, x = 0, y = 0):
        if winName:
            acc = None
            for gui in self._list_guis():
                if self._match_name_to_acc(winName, gui):
                    if 'Component' in pyatspi.listInterfaces(gui):
                        acc = gui
                        break
            if not acc:
                raise LdtpServerException('No window matches %s' % winName)
            icomponent = acc.queryComponent()
            bb = icomponent.getExtents(pyatspi.DESKTOP_COORDS)
            x, y, resolution2, resolution1 = bb.x, bb.y, bb.height, bb.width

        window = gtk.gdk.get_default_root_window ()
        size = window.get_size ()
        pb = gtk.gdk.Pixbuf (gtk.gdk.COLORSPACE_RGB, False, 8, 
                             resolution1 or size [0], 
                             resolution2 or size [1])
        pb = pb.get_from_drawable (window, window.get_colormap (),
                                   x, y, 0, 0, 
                                   resolution1 or size [0], 
                                   resolution2 or size [1])

        if pb:
            tmpFile = tempfile.mktemp('.png', 'ldtpd_')
            pb.save(tmpFile, 'png')
            del pb
            gc.collect()
        rv = b64encode(open(tmpFile).read())
        os.remove(tmpFile)
        return rv
