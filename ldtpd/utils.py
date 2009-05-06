import pyatspi
from constants import abbreviated_roles
import gobject
from fnmatch import translate as glob_trans
from re import match as re_match

class Utils:
    def __init__(self):
        self._desktop = pyatspi.Registry.getDesktop(0)

    def _list_guis(self):
        for app in self._desktop:
            if not app: continue
            for gui in app:
                if not gui: continue
                yield gui

    def _ldtpize_accessible(self, acc):
        label_acc = None
        if not acc.name:
            rel_set = acc.getRelationSet()
            for i, rel in enumerate(rel_set):
                if rel.getRelationType() == pyatspi.RELATION_LABELLED_BY:
                    label_acc = rel.getTarget(i)
                    break
        return abbreviated_roles.get(acc.getRole(), 'ukn'), \
            (label_acc or acc).name.replace(' ', '').rstrip(':')

    def _glob_match(self, pattern, string):
        return bool(re_match(glob_trans(pattern), string))

    def _match_name_to_acc(self, name, acc):
        if acc.name == name:
            return 1
        _object_name = self._ldtpize_accessible(acc)
        _object_name = '%s%s' % (_object_name[0],_object_name[1])
        if _object_name  == name:
            return 1
        if self._glob_match(name, acc.name):
            return 1
        if self._glob_match(name, _object_name):
            return 1
        return 0

    def _list_objects(self, obj):
        if obj:
            yield obj
            for child in obj:
                for c in self._list_objects(child):
                    yield c

    def _appmap_pairs(self, gui):
        ldtpized_list = []
        for obj in self._list_objects(gui):
            abbrev_role, abbrev_name = self._ldtpize_accessible(obj)
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

    def _click_object(self, obj, action = 'click'):
        try:
            iaction = obj.queryAction()
        except NotImplementedError:
            raise LdtpServerException(
                'Object does not have an Action interface')
        else:
            for i in xrange(iaction.nActions):
                if iaction.getName(i) == action:
                    iaction.doAction(i)
                    return
            raise LdtpServerException('Object does not have a "click" action')

    def _get_object(self, window_name, obj_name):
        for gui in self._list_guis():
            if self._match_name_to_acc(window_name, gui):
                for name, obj in self._appmap_pairs(gui):
                    if self._match_name_to_acc (obj_name, obj):
                        return obj
        raise LdtpServerException(
            'Unable to find object name in application map')

    def _grab_focus(self, obj):
        try:
            componenti = obj.queryComponent()
        except:
            raise LdtpServerException('Failed to grab focus for %s' % obj)
        componenti.grabFocus()

    def _check_state (self, window_name, obj, object_state):
        _state = obj.getState()
        _current_state = _state.getStates()

        _status = False
        if object_state in _current_state:
            _status = True

        return _status
