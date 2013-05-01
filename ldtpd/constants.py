"""
LDTP v2 constants.

@author: Eitan Isaacson <eitan@ascender.com>
@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@copyright: Copyright (c) 2009-13 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See 'COPYING' in the source distribution for more information.

Headers in this file shall remain intact.
"""

import pyatspi

abbreviated_roles = {
    pyatspi.ROLE_PAGE_TAB : 'ptab',
    pyatspi.ROLE_PAGE_TAB_LIST : 'ptl',
    pyatspi.ROLE_TABLE : 'tbl',
    pyatspi.ROLE_COMBO_BOX : 'cbo',
    pyatspi.ROLE_SPIN_BUTTON : 'sbtn',
    pyatspi.ROLE_FONT_CHOOSER : 'dlg',
    pyatspi.ROLE_COLOR_CHOOSER : 'dlg',
    pyatspi.ROLE_RADIO_BUTTON : 'rbtn',
    pyatspi.ROLE_TREE : 'tree',
    pyatspi.ROLE_TREE_TABLE : 'ttbl',
    pyatspi.ROLE_LAYERED_PANE : 'pane',
    pyatspi.ROLE_ICON : 'ico',
    pyatspi.ROLE_FRAME : 'frm',
    pyatspi.ROLE_DIALOG : 'dlg',
    pyatspi.ROLE_WINDOW : 'dlg',
    pyatspi.ROLE_FILE_CHOOSER : 'dlg',
    pyatspi.ROLE_ALERT : 'dlg',
    pyatspi.ROLE_CALENDAR : 'cal',
    pyatspi.ROLE_PANEL : 'pnl',
    pyatspi.ROLE_LABEL : 'lbl',
    pyatspi.ROLE_MENU_BAR : 'mbr',
    pyatspi.ROLE_MENU : 'mnu',
    pyatspi.ROLE_MENU_ITEM : 'mnu',
    pyatspi.ROLE_LIST_ITEM : 'lst',
    pyatspi.ROLE_LIST : 'lst',
    pyatspi.ROLE_CHECK_MENU_ITEM : 'mnu',
    pyatspi.ROLE_RADIO_MENU_ITEM : 'mnu',
    pyatspi.ROLE_PUSH_BUTTON : 'btn',
    pyatspi.ROLE_TOGGLE_BUTTON : 'tbtn',
    pyatspi.ROLE_SCROLL_BAR : 'scbr',
    pyatspi.ROLE_SCROLL_PANE : 'scpn',
    pyatspi.ROLE_TEXT : 'txt',
    pyatspi.ROLE_ENTRY : 'txt',
    pyatspi.ROLE_AUTOCOMPLETE : 'auto',
    pyatspi.ROLE_PARAGRAPH : 'txt',
    pyatspi.ROLE_PASSWORD_TEXT : 'txt',
    pyatspi.ROLE_STATUS_BAR : 'stat',
    pyatspi.ROLE_EDITBAR : 'txt',
    pyatspi.ROLE_TABLE_COLUMN_HEADER : 'tch',
    pyatspi.ROLE_SEPARATOR : 'spr',
    pyatspi.ROLE_FILLER : 'flr',
    pyatspi.ROLE_CANVAS : 'cnvs',
    pyatspi.ROLE_SPLIT_PANE : 'splt',
    pyatspi.ROLE_SLIDER : 'sldr',
    pyatspi.ROLE_HTML_CONTAINER : 'html',
    pyatspi.ROLE_PROGRESS_BAR : 'pbar',
    pyatspi.ROLE_TOOL_BAR : 'tbar',
    pyatspi.ROLE_TOOL_TIP : 'ttip',
    pyatspi.ROLE_CHECK_BOX : 'chk',
    pyatspi.ROLE_TABLE_CELL : 'tblc',
    pyatspi.ROLE_OPTION_PANE : 'opane',
    pyatspi.ROLE_POPUP_MENU : 'popmnu',
    pyatspi.ROLE_EMBEDDED : 'emb'}
