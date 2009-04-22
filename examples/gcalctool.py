import ldtp
from time import sleep
import unittest

class WidgetTestCase(unittest.TestCase):
    def setUp(self):
        ldtp.launchapp('gcalctool')
        ldtp.waittillguiexist('frmCalculator*')

    def tearDown(self):
        ldtp.selectmenuitem('frmCalculator*', 'mnuQuit')
        ldtp.waittillguinotexist('frmCalculator*')

    def testViews(self):
        ldtp.selectmenuitem('frmCalculator*', 'mnuAdvanced')
        sleep(1)
        ldtp.selectmenuitem('frmCalculator*', 'mnuFinancial')
        sleep(1)
        ldtp.selectmenuitem('frmCalculator*', 'mnuScientific')
        sleep(1)
        ldtp.selectmenuitem('frmCalculator*', 'mnuProgramming')
        sleep(1)
        ldtp.selectmenuitem('frmCalculator*', 'mnuBasic')

    def testInteraction(self):
        ldtp.click('frmCalculator*', 'btnNumeric1')
        sleep(0.5)
        ldtp.click('frmCalculator*', 'btnNumeric2')
        sleep(0.5)
        ldtp.click('frmCalculator*', 'btnNumeric3')
        sleep(0.5)
        ldtp.click('frmCalculator*', 'btnNumeric4')
        sleep(0.5)
        ldtp.click('frmCalculator*', 'btnMultiply')
        sleep(0.5)
        ldtp.click('frmCalculator*', 'btnNumeric2')
        sleep(0.5)
        ldtp.click('frmCalculator*', 'btnCalculateresult')

if __name__ == '__main__':
    unittest.main()
