"""
# Refer http://nagappanal.blogspot.com/2012/04/select-element-in-system-tray-windows-7.html

@author: Nagappan Alagappan <nagappan@gmail.com>
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

from ldtp import *

s=getobjectsize('pane0', 'btnNotificationChevron')
generatemouseevent(s[0] + s[2]/2, s[1] + s[3]/2, 'b1c')
wait(2)
s1=getobjectsize('paneNotificationOverflow', 'btnMcAffee*')
generatemouseevent(s1[0] + s1[2]/2, s1[1] + s1[3]/2, 'b3c')
wait(2)
getobjectlist('mnuContext')
selectmenuitem('mnuContext', 'mnuVirusScanConsole')
