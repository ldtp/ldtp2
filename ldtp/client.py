import xmlrpclib
from socket import error as SocketError
from time import sleep
import subprocess
import sys

class LdtpClient(xmlrpclib.ServerProxy):
    def __init__(self, uri, encoding=None, verbose=0, use_datetime=0):
        xmlrpclib.ServerProxy.__init__(
            self, uri, Transport(), encoding, verbose, 1, use_datetime)

class Transport(xmlrpclib.Transport):
    def _spawn_daemon(self):
        self._daemon = subprocess.Popen(
            ['python', '-c', 'import ldtpd; ldtpd.main()'],
            stderr=sys.stderr)
        sleep(2)

    def request(self, host, handler, request_body, verbose=0):
        try:
            return xmlrpclib.Transport.request(
                self, host, handler, request_body, verbose=0)
        except SocketError, e:
            if e.errno == 111 and 'localhost' in host:
                self._spawn_daemon()
                return xmlrpclib.Transport.request(
                    self, host, handler, request_body, verbose=0)
            raise

    def __del__(self):
        try:
            self._daemon.kill()
        except AttributeError:
            pass

_client = LdtpClient('http://localhost:4118')
