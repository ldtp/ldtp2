'''
Keypress actions.

@author: Eitan Isaacson
@copyright: Copyright (c) 2007 - 2009 Eitan Isaacson
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See "COPYING" in the source distribution for more information.

Headers in this file shall remain intact.
'''

import pyatspi
import gtk
from sequence_step import AtomicAction
import gobject
import utils
_ = lambda x: x

# Highest granularity, define timing for every single press and release

# Minimum delta time
min_delta = 50

# Maximum time before a key release
release_max = 400

keymap = gtk.gdk.keymap_get_default()

class KeyPressAction(AtomicAction):
  '''
  A key press step. Emulates a keyboard key press.
  '''
  def __init__(self, delta_time, key_code=None, key_name=None):
    '''
    Initialize L{KeyPressAction}. Could use either a hardware keycode, 
    a key name, or both.
    
    @param delta_time: Time to wait before performing this step.
    @type delta_time: integer
    @param key_code: Hardware keycode.
    @type key_code: integer.
    @param key_name: Key name.
    @type key_name: string.
    '''
    if (None, None) == (key_name, key_code):
      raise TypeError("Need either a key code or a key name")
    if delta_time > release_max: delta_time = release_max
    self._key_name = key_name
    if key_code is None:
      key_code = utils.getKeyCodeFromVal(gtk.gdk.keyval_from_name(key_name))
    AtomicAction.__init__(self, delta_time, self._keyPress, key_code)

  def _keyPress(self, key_code):
    '''
    Perform actual key press.
    
    @param key_code: Hardware key code.
    @type key_code: integer
    '''
    pyatspi.Registry.generateKeyboardEvent(key_code, None, pyatspi.KEY_PRESS)

  def __str__(self):
    '''
    String representation of instance.

    @return: String representation of instance.
    @rtype: string
    '''
    return _('Key press %s') % self._key_name or 'a key'

class KeyReleaseAction(AtomicAction):
  '''
  A key release step. Emulates a keyboard key release.
  '''
  def __init__(self, delta_time, key_code=None, key_name=None):
    '''
    Initialize L{KeyReleaseAction}. Could use either a hardware keycode, 
    a key name, or both.
    
    @param delta_time: Time to wait before performing this step.
    @type delta_time: integer
    @param key_code: Hardware keycode.
    @type key_code: integer.
    @param key_name: Key name.
    @type key_name: string.
    '''
    if (None, None) == (key_name, key_code):
      raise TypeError("Need either a key code or a key name")
    if delta_time > release_max: delta_time = release_max
    self._key_name = key_name
    if key_code is None:
      key_code = utils.getKeyCodeFromVal(gtk.gdk.keyval_from_name(key_name))
    AtomicAction.__init__(self, delta_time, self._keyRelease, key_code)

  def _keyRelease(self, key_code):
    '''
    Perform actual key release.
    
    @param key_code: Hardware key code.
    @type key_code: integer
    '''
    pyatspi.Registry.generateKeyboardEvent(key_code, None, pyatspi.KEY_RELEASE)

  def __str__(self):
    '''
    String representation of instance.

    @return: String representation of instance.
    @rtype: string
    '''
    return _('Key release %s') % self._key_name or 'a key'


# A bit smarter about common interactions.

keystroke_interval = 10
mod_key_code_mappings = {
  'GDK_CONTROL_MASK' : 37,
  'GDK_MOD1_MASK' : 64,
  'GDK_LOCK_MASK' : 66,
  'GDK_SHIFT_MASK' : 50
  }

class KeyComboAction(AtomicAction):
  '''
  Key combo action. Performs a press and release of a single or key combination.

  @ivar _key_combo: Name of key combination or single key press-release.
  @type _key_combo: string
  '''
  def __init__(self, key_combo, delta_time=0):    
    '''
    Initialize L{KeyComboAction}.
    
    @param key_combo: Name of key combination or single key press-release.
    @type key_combo: string
    @param delta_time: Time to wait before performing step.
    @type delta_time: integer
    '''
    keyval, modifiers = gtk.accelerator_parse(key_combo)
    key_code = utils.getKeyCodeFromVal(keyval)
    self._key_combo = key_combo
    if delta_time < min_delta: delta_time = min_delta
    AtomicAction.__init__(self, delta_time, self._doCombo, key_code, modifiers)

  def __call__(self):
    '''
    Perform step. Overridden to omit L{SequenceStep.stepDone}.
    '''
    self._func(*self._args)

  def _doCombo(self, key_code, modifiers):
    '''
    Perform combo operation.
    
    @param key_code: Key code to press.
    @type key_code: integer
    @param modifiers: Modifier mask to press with.
    @type modifiers: integer
    '''
    interval = 0
    mod_hw_codes = map(mod_key_code_mappings.get, modifiers.value_names)
    for mod_hw_code in mod_hw_codes:
      gobject.timeout_add(interval, self._keyPress, mod_hw_code)
      interval += keystroke_interval
    gobject.timeout_add(interval, self._keyPressRelease, key_code)
    interval += keystroke_interval
    mod_hw_codes.reverse()
    for mod_hw_code in mod_hw_codes:
      gobject.timeout_add(interval, self._keyRelease, mod_hw_code)
      interval += keystroke_interval
    gobject.timeout_add(interval, self.stepDone)

  def _keyPress(self, hw_code):
    '''
    Press modifier key.
    
    @param hw_code: Hardware code for key.
    @type hw_code: integer
    '''
    pyatspi.Registry.generateKeyboardEvent(hw_code, None, pyatspi.KEY_PRESS)
    return False

  def _keyRelease(self, hw_code):
    '''
    Release modifier key.
    
    @param hw_code: Hardware code for key.
    @type hw_code: integer
    '''
    pyatspi.Registry.generateKeyboardEvent(hw_code, None, pyatspi.KEY_RELEASE)
    return False

  def _keyPressRelease(self, keyval):
    '''
    Press and release non-modifier key.
    
    @param key_code: Key code.
    @type key_code: integer
    '''
    pyatspi.Registry.generateKeyboardEvent(keyval, None, 
                                           pyatspi.KEY_PRESSRELEASE)
    return False

  def __str__(self):
    '''
    String representation of instance.

    @return: String representation of instance.
    @rtype: string
    '''
    return _('Press %s') % self._key_combo

class TypeAction(AtomicAction):
  '''
  Type a sequence of characters.
  '''
  def __init__(self, string_to_type, delta_time=0, interval=None):    
    '''
    Initialize L{TypeAction}
    
    @param string_to_type: String to type.
    @type string_to_type: string
    @param delta_time: time before starting this step.
    @type delta_time: integer
    @param interval: Time between keystrokes.
    @type interval: integer
    '''
    self._string_to_type = string_to_type
    if interval:
      self.interval = interval
    else:
      self.interval = keystroke_interval
    if delta_time < min_delta: delta_time = min_delta
    AtomicAction.__init__(self, delta_time, self._doType, string_to_type)

  def __call__(self):
    '''
    Perform step. Overridden to omit L{SequenceStep.stepDone}.
    '''
    self._func(*self._args)

  def _doType(self, string_to_type):
    '''
    Do typing action.
    
    @param string_to_type: String to type.
    @type string_to_type: string
    '''
    interval = 0
    for char in string_to_type:
      gobject.timeout_add(interval, self._charType, 
                          gtk.gdk.unicode_to_keyval(ord(char)))
      interval += self.interval 
    gobject.timeout_add(interval, self.stepDone)

  def _charType(self, keyval):
    '''
    Type a single character.
    
    @param keyval: Key code to type.
    @type keyval: intger
    '''
    key_code, group, level = keymap.get_entries_for_keyval(keyval)[0]
    if level == 1:
        pyatspi.Registry.generateKeyboardEvent(50, None, 
                                               pyatspi.KEY_PRESS)
    pyatspi.Registry.generateKeyboardEvent(key_code, None, 
                                           pyatspi.KEY_PRESSRELEASE)
    if level == 1:
        pyatspi.Registry.generateKeyboardEvent(50, None, 
                                               pyatspi.KEY_RELEASE)
    return False

  def __str__(self):
    '''
    String representation of instance.

    @return: String representation of instance.
    @rtype: string
    '''
    return _('Type %s') % self._string_to_type

if __name__ == "__main__":
    type_action = TypeAction("Hello world!")
    type_action()
    gobject.MainLoop().run()
