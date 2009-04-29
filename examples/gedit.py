import ldtp, ooldtp
from time import sleep

ldtp.launchapp('gedit')

frm = ooldtp.context('*gedit')
frm.waittillguiexist()
txt_field = frm.getchild('txt1')
txt_field.enterstring('Hello world!')
sleep(3)
mnu_quit = frm.getchild('mnuQuit')
mnu_quit.selectmenuitem()
alert = ooldtp.context('Question')
alert.waittillguiexist()
btn = alert.getchild('btnClosewithoutSaving')
btn.click()
frm.waittillguinotexist()
