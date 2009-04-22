from twisted.internet import reactor
from twisted.web import server
from daemon import Ldtpd
import pyatspi

def main(port=4118):
    pyatspi.setCacheLevel(pyatspi.CACHE_PROPERTIES)
    r = Ldtpd()
    reactor.listenTCP(port, server.Site(r))
    reactor.run()
