import pyatspi
from constants import abbreviated_roles
import gobject

def list_guis(desktop):
    guis = []
    for app in desktop:
        if not app: continue
        for gui in app:
            if not gui: continue
            guis.append(gui)
    return guis


def ldtpize_accessible(acc):
    return '%s%s' % (abbreviated_roles.get(acc.getRole(), 'ukn'), 
                     acc.name.replace(' ', ''))

def match_name_to_acc(name, acc):
    if acc.name == name:
        return 1
    if ldtpize_accessible(acc) == name:
        return 1
    return 0


