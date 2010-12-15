'''
LDTP v2 Core Value.

@author: Eitan Isaacson <eitan@ascender.com>
@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@copyright: Copyright (c) 2009 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See "COPYING" in the source distribution for more information.

Headers in this file shall remain intact.
'''
import time
import pyatspi 
from utils import Utils
from server_exception import LdtpServerException

class Value(Utils):
    def setvalue(self, window_name, object_name, data):
        '''
        Type string sequence.
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param data: data to type.
        @type data: double

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        valuei.currentValue = float(data)
        return 1

    def getvalue(self, window_name, object_name):
        '''
        Get object value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: value on success.
        @rtype: double
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        return valuei.currentValue

    def getslidervalue(self, window_name, object_name):
        '''
        Get slider value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: value on success.
        @rtype: double
        '''
        return self.getvalue(window_name, object_name)

    def verifysetvalue(self, window_name, object_name, data):
        '''
        Get object value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param data: data to verify.
        @type data: double

        @return: 1 on success 0 on failure.
        @rtype: 1
        '''
        try:
            obj = self._get_object(window_name, object_name)
            valuei = obj.queryValue()

            if valuei.currentValue == data:
                return 1
        except:
            pass
        return 0

    def getminvalue(self, window_name, object_name):
        '''
        Get object min value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: float value on success.
        @rtype: double
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        return valuei.minimumValue

    def getminincrement(self, window_name, object_name):
        '''
        Get object min increment value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: float value on success.
        @rtype: double
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        return valuei.minimumIncrement

    def getmaxvalue(self, window_name, object_name):
        '''
        Get object max value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: float value on success.
        @rtype: double
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        return valuei.maximumValue

    # Name compatibility with setmax
    getmax = getmaxvalue

    def verifyslidervertical(self, window_name, object_name):
        '''
        Verify slider is vertical
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        try:
            obj = self._get_object(window_name, object_name)

            if self._check_state(obj, pyatspi.STATE_VERTICAL):
                return 1
        except:
            pass
        return 0

    def verifysliderhorizontal(self, window_name, object_name):
        '''
        Verify slider is horizontal
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        try:
            obj = self._get_object(window_name, object_name)

            if self._check_state(obj, pyatspi.STATE_HORIZONTAL):
                return 1
        except:
            pass
        return 0

    def verifyscrollbarvertical(self, window_name, object_name):
        '''
        Verify scrollbar is vertical
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        try:
            obj = self._get_object(window_name, object_name)

            if self._check_state(obj, pyatspi.STATE_VERTICAL):
                return 1
        except:
            pass
        return 0

    def verifyscrollbarhorizontal(self, window_name, object_name):
        '''
        Verify scrollbar is horizontal
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        try:
            obj = self._get_object(window_name, object_name)

            if self._check_state(obj, pyatspi.STATE_HORIZONTAL):
                return 1
        except:
            pass
        return 0

    def scrollup(self, window_name, object_name):
        '''
        Scroll up
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        if not self.verifyscrollbarvertical(window_name, object_name):
            raise LdtpServerException('Object not vertical scrollbar')
        return self.setmin(window_name, object_name)

    def scrolldown(self, window_name, object_name):
        '''
        Scroll down
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        if not self.verifyscrollbarvertical(window_name, object_name):
            raise LdtpServerException('Object not vertical scrollbar')
        return self.setmax(window_name, object_name)

    def scrollleft(self, window_name, object_name):
        '''
        Scroll left
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        if not self.verifyscrollbarhorizontal(window_name, object_name):
            raise LdtpServerException('Object not horizontal scrollbar')
        return self.setmin(window_name, object_name)

    def scrollright(self, window_name, object_name):
        '''
        Scroll right
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        if not self.verifyscrollbarhorizontal(window_name, object_name):
            raise LdtpServerException('Object not horizontal scrollbar')
        return self.setmax(window_name, object_name)

    def setmax(self, window_name, object_name):
        '''
        Set max value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        valuei.currentValue = valuei.maximumValue
        return 1

    def setmin(self, window_name, object_name):
        '''
        Set min value
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        valuei.currentValue = valuei.minimumValue
        return 1

    def increase(self, window_name, object_name, iterations):
        '''
        Increase slider with number of iterations
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param object_name: iterations to perform on slider increase
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        i = 0
        flag = False
        while i < iterations:
            if valuei.currentValue >= valuei.maximumValue:
                raise LdtpServerException('Maximum limit reached')
            valuei.currentValue += 1.0
            time.sleep(1.0/100)
            flag = True
            i += 1
        if flag:
            return 1
        else:
            raise LdtpServerException('Unable to increase slider value')

    def decrease(self, window_name, object_name, iterations):
        '''
        Decrease slider with number of iterations
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param object_name: iterations to perform on slider decrease
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        i = 0
        flag = False
        while i < iterations:
            if valuei.currentValue >= valuei.minimumValue:
                raise LdtpServerException('Maximum limit reached')
            valuei.currentValue -= 1.0
            time.sleep(1.0/100)
            flag = True
            i += 1
        if flag:
            return 1
        else:
            raise LdtpServerException('Unable to decrease slider value')

    def onedown(self, window_name, object_name, iterations):
        '''
        Press scrollbar down with number of iterations
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param object_name: iterations to perform on slider increase
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        if not self.verifyscrollbarvertical(window_name, object_name):
            raise LdtpServerException('Object not vertical scrollbar')

        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        i = 0
        maxValue = valuei.maximumValue / 8;
        flag = False
        while i < iterations:
            if valuei.currentValue >= valuei.maximumValue:
                raise LdtpServerException('Maximum limit reached')
            valuei.currentValue += maxValue
            time.sleep(1.0/100)
            flag = True
            i += 1
        if flag:
            return 1
        else:
            raise LdtpServerException('Unable to increase scrollbar')

    def oneup(self, window_name, object_name, iterations):
        '''
        Press scrollbar up with number of iterations
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param object_name: iterations to perform on slider increase
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        if not self.verifyscrollbarvertical(window_name, object_name):
            raise LdtpServerException('Object not vertical scrollbar')

        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        i = 0
        minValue = valuei.maximumValue / 8
        flag = False
        while i < iterations:
            if valuei.currentValue < valuei.minimumValue:
                raise LdtpServerException('Minimum limit reached')
            valuei.currentValue -= minValue
            time.sleep(1.0/100)
            flag = True
            i += 1
        if flag:
            return 1
        else:
            raise LdtpServerException('Unable to decrease scrollbar')

    def oneright(self, window_name, object_name, iterations):
        '''
        Press scrollbar right with number of iterations
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param object_name: iterations to perform on slider increase
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        if not self.verifyscrollbarhorizontal(window_name, object_name):
            raise LdtpServerException('Object not horizontal scrollbar')

        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        i = 0
        max = valuei.maximumValue / 8;
        flag = False
        while i < iterations:
            if valuei.currentValue >= valuei.maximumValue:
                raise LdtpServerException('Maximum limit reached')
            valuei.currentValue += max
            time.sleep(1.0/100)
            flag = True
            i += 1
        if flag:
            return 1
        else:
            raise LdtpServerException('Unable to increase scrollbar')

    def oneleft(self, window_name, object_name, iterations):
        '''
        Press scrollbar left with number of iterations
        
        @param window_name: Window name to type in, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to type in, either full name,
        LDTP's name convention, or a Unix glob. 
        @type object_name: string
        @param object_name: iterations to perform on slider increase
        @type object_name: integer

        @return: 1 on success.
        @rtype: integer
        '''
        if not self.verifyscrollbarhorizontal(window_name, object_name):
            raise LdtpServerException('Object not horizontal scrollbar')

        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Value cannot be entered into object.')

        i = 0
        min = valuei.maximumValue / 8;
        flag = False
        while i < iterations:
            if valuei.currentValue < valuei.minimumValue:
                raise LdtpServerException('Minimum limit reached')
            valuei.currentValue -= min
            time.sleep(1.0/100)
            flag = True
            i += 1
        if flag:
            return 1
        else:
            raise LdtpServerException('Unable to decrease scrollbar')
