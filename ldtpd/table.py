import pyatspi 
from utils import Utils

class Table(Utils):
    def getrowcount(self, window_name, object_name):
        '''
        Get count of rows in table object.
        
        @param window_name: Window name to look for, either full name,
        LDTP's name convention, or a Unix glob.
        @type window_name: string
        @param object_name: Object name to look for, either full name,
        LDTP's name convention, or a Unix glob. Or menu heirarchy
        @type object_name: string

        @return: Number of rows.
        @rtype: integer
        '''
        obj = self._get_object(window_name, object_name)

        try:
            itable = obj.queryTable()
        except NotImplementedError:
            raise LdtpServerException('object %s is not a table' % object_name)

        return itable.nRows
