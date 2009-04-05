import client

def whoismyhost():
    return client._client._ServerProxy__host

def launchapp(cmdline):
    return client._client.launchapp(cmdline)

def guiexist(gui_name, object_name=None):
    return client._client.guiexist(gui_name, object_name)
