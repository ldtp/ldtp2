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
import tempfile
from base64 import b64decode
from client_exception import LdtpExecutionError

class AccessibilityState:
    pass

state = AccessibilityState()

def setHost(uri):
    client._client = client.LdtpClient(uri)

def whoismyhost():
    return client._client._ServerProxy__host

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

def imagecapture(winName = None, outFile = None, resolution1 = None,
                 resolution2 = None, x = 0, y = 0):
    if not outFile:
        outFile = tempfile.mktemp('.png', 'ldtp_')
        
    data = _remote_imagecapture(winName, resolution1, resolution2, x, y)
    f = open(outFile, 'w')
    f.write(b64decode(data))
    f.close()

    return outFile

def get_all_state_names():
    """
    Just a local function to replicate the key / value of state class
    """
    _all_states = _remote_get_all_state_names()
    # Based on
    # http://rosettacode.org/wiki/Adding_variables_to_a_class_instance_at_runtime#Python
    for _current_state in _all_states:
        # From dictionary, populate the state class members at run-time
        # pyatspi convention - state.STATE_INVALID
        setattr(state, _current_state, _all_states[_current_state])
        # LDTP convention - state.INVALID
        setattr(state, _current_state[_current_state.find('_')+1:],
                _all_states[_current_state])

_populateNamespace(globals())
get_all_state_names()

# Remove this function, as we don't use it later, once the data is populated
del globals()['get_all_state_names']

atexit.register(client._client.kill_daemon)
