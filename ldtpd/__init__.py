"""
LDTP v2 init file

@author: Eitan Isaacson <eitan@ascender.com>
@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@copyright: Copyright (c) 2009-14 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See 'COPYING' in the source distribution for more information.

Headers in this file shall remain intact.
"""

class SignalParent:
    def __init__(self, parentpid):
        from twisted import internet
        self.parentpid = parentpid
        self.reactor = internet.reactor

    def send_later(self):
        self.reactor.callLater(1, self.send)

    def send(self):
        import os
        import signal

        os.kill(int(self.parentpid), signal.SIGUSR1)

def main(port=4118, parentpid=None):
    import os
    os.environ['NO_GAIL'] = '1'
    os.environ['NO_AT_BRIDGE'] = '1'

    import twisted
    gtkVersion = None
    try:
        from gi.repository import Gtk
        gtkVersion = Gtk._version
    except:
        pass
    if not gtkVersion or gtkVersion == '2.0':
       # As per Ubuntu 11.10, twisted glib2reactor
       # works with gtk2, which fails with gtk3
       from twisted.internet import glib2reactor
       glib2reactor.install()
    elif gtkVersion >= '3.0':
        try:
            # Exist in Ubuntu 12.04, but not on
            # Ubuntu 11.10 / Fedora 16
            from twisted.internet import gtk3reactor
            gtk3reactor.install()
        except:
            pass
    from twisted.internet import reactor
    from twisted.web import server, xmlrpc
    from xmlrpc_daemon import XMLRPCLdtpd
    import twisted.internet
    import socket
    import pyatspi
    import traceback

    _ldtp_debug = os.environ.get('LDTP_DEBUG', None)
    _ldtp_debug_file = os.environ.get('LDTP_DEBUG_FILE', None)

    try:
        pyatspi.setCacheLevel(pyatspi.CACHE_PROPERTIES)
        r = XMLRPCLdtpd()
        xmlrpc.addIntrospection(r)
        if parentpid:
            reactor.callWhenRunning(SignalParent(parentpid).send_later)
        reactor.listenTCP(port, server.Site(r))
        reactor.run()
    except twisted.internet.error.CannotListenError:
        if _ldtp_debug:
            print(traceback.format_exc())
    except socket.error:
        if _ldtp_debug:
            print(traceback.format_exc())
        if _ldtp_debug_file:
            with open(_ldtp_debug_file, "a") as fp:
                fp.write(traceback.format_exc())
