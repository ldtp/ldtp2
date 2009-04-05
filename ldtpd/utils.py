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
    pyatspi.ROLE_EMBEDDED : 'emb'}

def ldtpize_accessible(acc):
    return '%s%s' % (abbreviated_roles.get(acc.getRole(), 'ukn'), 
                     acc.name.replace(' ', ''))

def match_name_to_acc(name, acc):
    if acc.name == name:
        return 1
    if ldtpize_accessible(acc) == name:
        return 1
    return 0
