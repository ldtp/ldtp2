import pyatspi
from constants import abbreviated_roles
import gobject
from fnmatch import translate as glob_trans
from re import match as re_match

def list_guis(desktop):
    for app in desktop:
        if not app: continue
        for gui in app:
            if not gui: continue
            yield gui

def ldtpize_accessible(acc):
    return '%s%s' % (abbreviated_roles.get(acc.getRole(), 'ukn'), 
                     acc.name.replace(' ', ''))

def glob_match(pattern, string):
    return bool(re_match(glob_trans(pattern), string))


def match_name_to_acc(name, acc):
    if acc.name == name:
        return 1
    if ldtpize_accessible(acc) == name:
        return 1
    if glob_match(name, acc.name):
        return 1
    if glob_match(name, ldtpize_accessible(acc)):
        return 1
    return 0

def list_objects(obj):
    if obj:
        yield obj
        for child in obj:
            for c in list_objects(child):
                yield c

def appmap_pairs(gui):
    ldtpized_list = []
    for obj in list_objects(gui):
        ldtpized_name_base = ldtpize_accessible(obj)
        ldtpized_name = ldtpized_name_base
        i = 1
        while ldtpized_name in ldtpized_list:
            ldtpized_name = '%s%d' % (ldtpized_name_base, i)
            i += 1
        ldtpized_list.append(ldtpized_name)
        yield ldtpized_name, obj

if __name__ == "__main__":
    for g in list_guis(pyatspi.Registry.getDesktop(0)):
        for a, b in appmap_pairs(g):
            print a, b
        break
