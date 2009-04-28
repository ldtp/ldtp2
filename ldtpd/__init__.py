def main(port=4118):
    import os
    os.environ['NO_GAIL'] = '1'
    os.environ['NO_AT_BRIDGE'] = '1'

    from twisted.internet import glib2reactor
    glib2reactor.install()
    from twisted.internet import reactor
    from twisted.web import server, xmlrpc
    from xmlrpc_daemon import XMLRPCLdtpd
    import pyatspi

    pyatspi.setCacheLevel(pyatspi.CACHE_PROPERTIES)
    r = XMLRPCLdtpd()
    xmlrpc.addIntrospection(r)
    reactor.listenTCP(port, server.Site(r))
    reactor.run()
