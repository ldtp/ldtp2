import ldtp
from time import sleep

print ldtp.launchapp('gcalctool')
print ldtp.waittillguiexist('frmCalculator*', 'mnuEdit', 20)
sleep(2)
print ldtp.selectmenuitem('frmCalculator*', 'mnuQuit')
print ldtp.waittillguinotexist('frmCalculator*', 20)
