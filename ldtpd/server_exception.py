'''
LDTP v2 Server exception

@author: Eitan Isaacson <eitan@ascender.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See "COPYING" in the source distribution for more information.

Headers in this file shall remain intact.
'''

from twisted.web import xmlrpc

ERROR_CODE = 123

class LdtpServerException(xmlrpc.Fault):
    def __init__(self, message):
        xmlrpc.Fault.__init__(self, ERROR_CODE, message)
