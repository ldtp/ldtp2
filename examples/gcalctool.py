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
        for menu_item in ('mnuAdvanced',
                          'mnuFinancial',
                          'mnuScientific',
                          'mnuProgramming',
                          'mnuBasic'):
            ldtp.selectmenuitem('frmCalculator*', menu_item)
            sleep(1)

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
