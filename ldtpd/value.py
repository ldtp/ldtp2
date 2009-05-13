import pyatspi 
from utils import Utils

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
            raise LdtpServerException('Text cannot be entered into object.')

        valuei.currentValue = float (data)
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
        @rtype: float
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        return valuei.currentValue

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
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        if valuei.currentValue == data:
            return 1
        else:
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
        @rtype: float
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

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
        @rtype: float
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

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
        @rtype: float
        '''
        obj = self._get_object(window_name, object_name)

        try:
            valuei = obj.queryValue()
        except NotImplementedError:
            raise LdtpServerException('Text cannot be entered into object.')

        return valuei.maximumValue
