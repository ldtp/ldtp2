import client

def setHost(uri):
    client._client = client.LdtpClient(uri)

def whoismyhost():
    return client._client._ServerProxy__host

def _populateNamespace(d):
    for method in client._client.system.listMethods():
        if method.startswith('system.'):
            continue
        d[method] = getattr(client._client, method)
        d[method].__doc__ = client._client.system.methodHelp(method)

_populateNamespace(globals())
