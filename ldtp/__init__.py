import client
from functional import *

def setHost(uri):
    client._client = client.LdtpClient(uri)
