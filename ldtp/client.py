"""
LDTP v2 client

@author: Eitan Isaacson <eitan@ascender.com>
@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@copyright: Copyright (c) 2009-11 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See 'COPYING' in the source distribution for more information.

Headers in this file shall remain intact.
"""

import os
import sys
import time
import signal
import traceback
import xmlrpclib
import subprocess
import signal
from socket import error as SocketError
from client_exception import LdtpExecutionError, ERROR_CODE
from log import logger
from httplib import CannotSendRequest, ResponseNotReady

if 'LDTP_DEBUG' in os.environ:
    _ldtp_debug = os.environ['LDTP_DEBUG']
else:
    _ldtp_debug = None
if 'LDTP_SERVER_ADDR' in os.environ:
    _ldtp_server_addr = os.environ['LDTP_SERVER_ADDR']
else:
    _ldtp_server_addr = 'localhost'
if 'LDTP_SERVER_PORT' in os.environ:
    _ldtp_server_port = os.environ['LDTP_SERVER_PORT']
else:
    _ldtp_server_port = '4118'

class _Method(xmlrpclib._Method):
    def __call__(self, *args, **kwargs):
        logger.debug('%s(%s)' % (self.__name, \
                                 ', '.join(map(repr, args) + ['%s=%s' % (k, repr(v)) \
                                                              for k, v in kwargs.items()])))
        args += (kwargs,)
        return self.__send(self.__name, args)

class Transport(xmlrpclib.Transport):
    def _handle_signal(self, signum, frame):
        if _ldtp_debug:
            if signum == signal.SIGCHLD:
                print "ldtpd exited!"
            elif signum == signal.SIGUSR1:
                print "SIGUSR1 received. ldtpd ready for requests."
            elif signum == signal.SIGALRM:
                print "SIGALRM received. Timeout waiting for SIGUSR1."

    def _spawn_daemon(self):
        pid = os.getpid()
        pycmd = 'import ldtpd; ldtpd.main(parentpid=%s)' % pid
        self._daemon = os.spawnlp(os.P_NOWAIT, 'python',
                                  'python', '-c', pycmd)

    def request(self, host, handler, request_body, verbose=0):
        retry_count = 1
        while True:
            try:
                return xmlrpclib.Transport.request(
                    self, host, handler, request_body, verbose=0)
            except SocketError, e:
                if (e.errno == 111 or e.errno == 146) and 'localhost' in host:
                    if retry_count == 1:
                        retry_count += 1
                        sigusr1 = signal.signal(signal.SIGUSR1, self._handle_signal)
                        sigalrm = signal.signal(signal.SIGALRM, self._handle_signal)
                        sigchld = signal.signal(signal.SIGCHLD, self._handle_signal)
                        self._spawn_daemon()
                        signal.alarm(15) # Wait 15 seconds for ldtpd
                        signal.pause()
                        # restore signal handlers
                        signal.alarm(0)
                        signal.signal(signal.SIGUSR1, sigusr1)
                        signal.signal(signal.SIGALRM, sigalrm)
                        signal.signal(signal.SIGCHLD, sigchld)
                        continue
                    else:
                        raise
                # else raise exception
                raise
            except xmlrpclib.Fault, e:
                if e.faultCode == ERROR_CODE:
                    raise LdtpExecutionError(e.faultString.encode('utf-8'))
                else:
                    raise e
            except (CannotSendRequest, ResponseNotReady):
                # Use a clean connection and retry
                if retry_count < 10:
                    # In python 2.7 / Ubuntu Natty 11.04
                    # it fails, if this is not handled
                    # bug 638229
                    self.close()
                    retry_count += 1
                else:
                    raise

    def __del__(self):
        self.kill_daemon()

    def kill_daemon(self):
        try:
            os.kill(self._daemon, signal.SIGKILL)
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
