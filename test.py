import ldtp
print ldtp.launchapp('gcalctool')
print ldtp.waittillguiexist('frmCalculator', 'mnuEdit', 20)
