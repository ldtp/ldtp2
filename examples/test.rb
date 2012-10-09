require "ldtp"

ldtp = Ldtp.new('*-gedit')

#puts ldtp.launchapp('gedit')
#puts ldtp.wait(2)
#puts ldtp.selectmenuitem('File;Open')
#puts ldtp.waittillguinotexist :guiTimeOut => 5
#puts ldtp.click("btnOpen")
#ldtp.window_name = "dlgOpenFiles"
#puts ldtp.waittillguiexist(:obj_name => "btnCancel")
#puts ldtp.click("btnCancel")
#ldtp.window_name = "*-gedit"
#puts ldtp.selectmenuitem('File;Open')
#puts ldtp.imagecapture()
#puts ldtp.onwindowcreate("a", 'b', 1, 2, 3)
#puts ldtp.onwindowcreate("a", 'b', 1, 2, 3)
#puts ldtp.removecallback("a")
#puts ldtp.removecallback("x")
#puts ldtp.maximizewindow("*-gedit")
#puts ldtp.maximizewindow()
#puts ldtp.getapplist()
#puts ldtp.enterstring('Hello')
#puts ldtp.enterstring('*-gedit', 'txt1', 'Hello')
#puts ldtp.enterstring('', 'txt1', 'Hello')
#puts ldtp.settextvalue('txt1', 'Hello World')
#puts ldtp.gettextvalue('txt1')
#puts ldtp.getcharcount('txt1')
#puts ldtp.getcursorposition('txt1')
#puts ldtp.setcursorposition('txt1', 0)
#ldtp.window_name = 'Open Files'
#puts ldtp.doesrowexist("tblFiles", "Desktop")
#puts ldtp.doesrowexist("tblFiles", "Desk")
#puts ldtp.doesrowexist("tblFiles", "Desk", true)
puts ldtp.wait(3)
puts ldtp.getapplist()
