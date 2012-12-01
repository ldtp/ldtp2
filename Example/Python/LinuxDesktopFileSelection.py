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
# Executed this with Ubuntu 10.04 without Unity

# I created Test folder in desktop and made sure its visible
# 'dlg0' may not be same in your case, in our test scenario, I have tried like this:
# getwindowlist() before and after mouse right click, see whats the diff and use that
# to be even more precise, you can use for dlg with index
mouserightclick('frmx-nautilus-desktop', 'icoTest')
wait(1)
selectmenuitem('dlg0', 'mnuProperties')
