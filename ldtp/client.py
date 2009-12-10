'''
LDTP v2 client

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

import os
import sys
import time
import xmlrpclib
import subprocess
from socket import error as SocketError
from client_exception import LdtpExecutionError, ERROR_CODE
from log import logger

if os.environ.has_key('LDTP_SERVER_ADDR'):
    _ldtp_server_addr = os.environ['LDTP_SERVER_ADDR']
else:
    _ldtp_server_addr = 'localhost'
if os.environ.has_key('LDTP_SERVER_PORT'):
    _ldtp_server_port = os.environ['LDTP_SERVER_PORT']
else:
    _ldtp_server_port = '4118'

class _Method(xmlrpclib._Method):
    def __call__(self, *args, **kwargs):
        logger.debug('%s(%s)' % \
                         (self.__name, ', '.join(map(repr, args)+['%s=%s' % (k, repr(v)) for k, v in kwargs.items()])))
        args += (kwargs,)
        return self.__send(self.__name, args)
        
class Transport(xmlrpclib.Transport):
    def _spawn_daemon(self):
        self._daemon = subprocess.Popen(
            ['python', '-c', 'import ldtpd; ldtpd.main()'],
            close_fds = True)

    def request(self, host, handler, request_body, verbose=0):
        try:
            return xmlrpclib.Transport.request(
                self, host, handler, request_body, verbose=0)
        except SocketError, e:
            if e.errno == 111 and 'localhost' in host:
                self._spawn_daemon()
                time.sleep(2)
                # Retry connecting again
                return xmlrpclib.Transport.request(
                    self, host, handler, request_body, verbose=0)
            raise
        except xmlrpclib.Fault, e:
            if e.faultCode == ERROR_CODE:
                raise LdtpExecutionError(e.faultString)
            else:
                raise e

    def __del__(self):
        self.kill_daemon()

    def kill_daemon(self):
        try:
            self._daemon.kill()
        except AttributeError:
            pass

class LdtpClient(xmlrpclib.ServerProxy):
    def __init__(self, uri, encoding=None, verbose=0, use_datetime=0):
        xmlrpclib.ServerProxy.__init__(
            self, uri, Transport(), encoding, verbose, 1, use_datetime)

    def __getattr__(self, name):
        # magic method dispatcher
        return _Method(self._ServerProxy__request, name)

    def kill_daemon(self):
        self._ServerProxy__transport.kill_daemon()

    def setHost(self, host):
        setattr(self, '_ServerProxy__host', host)

_client = LdtpClient('http://%s:%s' % (_ldtp_server_addr, _ldtp_server_port))
