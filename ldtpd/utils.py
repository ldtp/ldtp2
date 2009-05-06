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
    label_acc = None
    if not acc.name:
        rel_set = acc.getRelationSet()
        for i, rel in enumerate(rel_set):
            if rel.getRelationType() == pyatspi.RELATION_LABELLED_BY:
                label_acc = rel.getTarget(i)
                break
    return abbreviated_roles.get(acc.getRole(), 'ukn'), \
        (label_acc or acc).name.replace(' ', '').rstrip(':')

def glob_match(pattern, string):
    return bool(re_match(glob_trans(pattern), string))

def match_name_to_acc(name, acc):
    if acc.name == name:
        return 1
    _object_name = ldtpize_accessible(acc)
    _object_name = '%s%s' % (_object_name[0],_object_name[1])
    if _object_name  == name:
        return 1
    if glob_match(name, acc.name):
        return 1
    if glob_match(name, _object_name):
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
        abbrev_role, abbrev_name = ldtpize_accessible(obj)
        if not abbrev_name:
            ldtpized_name_base = abbrev_role
            ldtpized_name = '%s0' % ldtpized_name_base
        else:
            ldtpized_name_base = '%s%s' % (abbrev_role, abbrev_name)
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
