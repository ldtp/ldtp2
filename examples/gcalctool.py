'''
LDTP v2 gcalctool example

@author: Eitan Isaacson <eitan@ascender.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See "COPYING" in the source distribution for more information.

Headers in this file shall remain intact.
'''

import ldtp
from time import sleep
import unittest

class WidgetTestCase(unittest.TestCase):
    def setUp(self):
        try:
            ldtp.launchapp('gcalctool')
            ldtp.waittillguiexist('frmCalculator*', guiTimeOut=5)
        except:
            self.tearDown()
            raise

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
