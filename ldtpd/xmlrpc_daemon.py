"""
LDTP v2 xml rpc daemon.

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

See "COPYING" in the source distribution for more information.

Headers in this file shall remain intact.
"""

import os
import re
import time
import core
import thread
from core import Ldtpd
from twisted.web import xmlrpc
import xmlrpclib
from log import logger

if 'LDTP_COMMAND_DELAY' in os.environ:
    delay = os.environ['LDTP_COMMAND_DELAY']
else:
    delay = None

if 'LDTP_DEBUG' in os.environ:
    _ldtp_debug = os.environ['LDTP_DEBUG']
else:
    _ldtp_debug = None

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
        xmlrpc.XMLRPC.__init__(self, allowNone = True)
        Ldtpd.__init__(self)
        self.args = self.kwargs = None

    def _listFunctions(self):
        return [a[7:] for a in \
                  filter(lambda x: x.startswith('xmlrpc_'), dir(self))]
    # Starting twisted 11.1
    listProcedures = _listFunctions

    if not _ldtp_debug:
        # If LDTP_DEBUG env set, then print verbose info on console
        def _ebRender(self, failure):
            """Custom error render method (used by our XMLRPC objects)"""
            if isinstance(failure.value, xmlrpclib.Fault):
                return failure.value

            if hasattr(failure, 'getErrorMessage'):
                value = failure.getErrorMessage()
            else:
                value = 'error'

            return xmlrpclib.Fault(self.FAILURE, value)

    def _ldtp_callback(self, request, function):
        try:
            xmlrpc.defer.maybeDeferred(function, *self.args, **self.kwargs).\
                addErrback(self._ebRender).\
                addCallback(self._cbRender, request)
        except:
            if ldtp_debug:
                print traceback.format_exc()

    def render_POST(self, request):
        request.content.seek(0, 0)
        request.setHeader("content-type", "text/xml")
        try:
            args, functionPath = xmlrpclib.loads(request.content.read())
            self.args = args
            if args and isinstance(args[-1], dict):
                # Passing args and kwargs to _ldtp_callback
                # fail, so using self, kind of work around !
                self.kwargs = args[-1]
                self.args = args[:-1]
                if delay or self._delaycmdexec:
                    pattern = '(wait|exist|has|get|verify|enabled|launch|image)'
                    p = re.compile(pattern)
                    if not p.search(functionPath):
                        # Sleep for 1 second, else the at-spi-registryd dies,
                        # on the speed we execute
                        try:
                            if self._delaycmdexec:
                                self.wait(float(self._delaycmdexec))
                            else:
                                self.wait(float(delay))
                        except ValueError:
                            time.sleep(0.5)
            else:
                self.kwargs = {}
        except Exception, e:
            f = xmlrpc.Fault(
                self.FAILURE, "Can't deserialize input: %s" % (e,))
            self._cbRender(f, request)
        else:
            try:
                if hasattr(self, 'lookupProcedure'):
                   # Starting twisted 11.1
                   function = self.lookupProcedure(functionPath)
                else:
                   function = self._getFunction(functionPath)
            except xmlrpc.Fault, f:
                self._cbRender(f, request)
            else:
                if _ldtp_debug:
                    debug_st = u'%s(%s)' % \
                        (functionPath,
                         ', '.join(map(repr, self.args) + \
                                       ['%s=%s' % (k, repr(v)) \
                                            for k, v in self.kwargs.items()]))
                    print debug_st
                    logger.debug(debug_st)
                if core.gtk3:
                    # In GTK3, with existing method, blocks
                    # parallel request, so starting the current
                    # client request in thread
                    thread.start_new_thread(self._ldtp_callback,
                                            (request, function))
                else:
                    xmlrpc.defer.maybeDeferred(function, *self.args,
                                               **self.kwargs).\
                                               addErrback(self._ebRender).\
                                               addCallback(self._cbRender,
                                                           request)
        return xmlrpc.server.NOT_DONE_YET
