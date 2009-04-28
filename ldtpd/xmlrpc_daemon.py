from core import Ldtpd
from twisted.web import xmlrpc

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

