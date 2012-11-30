from ldtp import *

launchapp('notepad')
waittillguiexist('*-Notepad')
selectmenuitem('*-Notepad', 'mnuFile;mnuExit')
waittillguinotexist('*-Notepad')
