import pyatspi
from constants import abbreviated_roles
import gobject

def list_guis(desktop):
    for app in desktop:
        if not app: continue
        for gui in app:
            if not gui: continue
            yield gui

def ldtpize_accessible(acc):
    return '%s%s' % (abbreviated_roles.get(acc.getRole(), 'ukn'), 
                     acc.name.replace(' ', ''))

def match_name_to_acc(name, acc):
    if acc.name == name:
        return 1
    if ldtpize_accessible(acc) == name:
        return 1
    return 0

def list_objects(obj):
    if obj:
        yield obj
        for child in obj:
            for c in list_objects(child):
                yield c

def appmap_pairs(gui, _ldtpized_list=[]):
    for obj in list_objects(gui):
        ldtpized_name_base = ldtpize_accessible(obj)
        ldtpized_name = ldtpized_name_base
        i = 1
        while ldtpized_name in _ldtpized_list:
            ldtpized_name = '%s%d' % (ldtpized_name_base, i)
            i += 1
        _ldtpized_list.append(ldtpized_name)
        yield ldtpized_name, obj

if __name__ == "__main__":
    for g in list_guis(pyatspi.Registry.getDesktop(0)):
        print g
        for a, b in appmap_pairs(g):
            print ' ', a, b
        break
