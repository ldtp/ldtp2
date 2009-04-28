from twisted.web import xmlrpc

ERROR_CODE = 123

class LdtpServerException(xmlrpc.Fault):
    def __init__(self, message):
        xmlrpc.Fault.__init__(self, ERROR_CODE, message)
