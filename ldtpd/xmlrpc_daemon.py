'''
LDTP v2 xml rpc daemon.

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

from core import Ldtpd
from twisted.web import xmlrpc
import xmlrpclib

class XMLRPCLdtpd(Ldtpd, xmlrpc.XMLRPC, object):
    def __new__(cls, *args, **kwargs):
        for symbol in dir(Ldtpd):
            if symbol.startswith('_'): 
                continue
            obj = getattr(cls, symbol)
            if not callable(obj):
                continue
            setattr(cls, 'xmlrpc_'+symbol, obj)
        return object.__new__(cls, *args, **kwargs)

    def __init__(self):
        xmlrpc.XMLRPC.__init__(self)
        Ldtpd.__init__(self)

    def _listFunctions(self):
        return [a[7:] for a in \
                  filter(lambda x: x.startswith('xmlrpc_'), dir(self))]


    def render_POST(self, request):
        request.content.seek(0, 0)
        request.setHeader("content-type", "text/xml")
        try:
            args, functionPath = xmlrpclib.loads(request.content.read())
            if args and isinstance(args[-1], dict):
                kwargs = args[-1]
                args = args[:-1]
            else:
                kwargs = {}
        except Exception, e:
            f = xmlrpc.Fault(
                self.FAILURE, "Can't deserialize input: %s" % (e,))
            self._cbRender(f, request)
        else:
            try:
                function = self._getFunction(functionPath)
            except xmlrpc.Fault, f:
                self._cbRender(f, request)
            else:
                xmlrpc.defer.maybeDeferred(function, *args, **kwargs).\
                    addErrback(self._ebRender).\
                    addCallback(self._cbRender, request)
        return xmlrpc.server.NOT_DONE_YET
