from twisted.internet import reactor
from twisted.web import server
from daemon import Ldtpd

def main(port=4118):
    r = Ldtpd()
    reactor.listenTCP(port, server.Site(r))
    reactor.run()
