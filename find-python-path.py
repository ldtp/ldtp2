#!/usr/bin/env python

import sys
from os.path import split, basename

def find_path ():
    for path in sys.path:
	(head, tail) = split (path)
        # Forcing python path to be used as /usr/lib instead of /usr/local/lib
	if (tail == 'site-packages' or tail == 'dist-packages') and \
                path.find ('local') == -1:
	    base = basename (head)
	    print path
	    #print base + '/' + tail
	    return

find_path ()
