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

import client
import atexit
from client_exception import LdtpExecutionError

def setHost(uri):
    client._client = client.LdtpClient(uri)

def whoismyhost():
    return client._client._ServerProxy__host

def _populateNamespace(d):
    for method in client._client.system.listMethods():
        if method.startswith('system.'):
            continue
        d[method] = getattr(client._client, method)
        d[method].__doc__ = client._client.system.methodHelp(method)

_populateNamespace(globals())

atexit.register(client._client.kill_daemon)
