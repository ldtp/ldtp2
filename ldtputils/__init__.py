"""
LDTP v2 ldtputils init file

@author: Eitan Isaacson <eitan@ascender.com>
@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009 Eitan Isaacson
@copyright: Copyright (c) 2009-12 Nagappan Alagappan
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of 
merchantability or fitness for a particular purpose.

See 'COPYING' in the source distribution for more information.

Headers in this file shall remain intact.
"""
import ldtp
from ldtp import imagecapture
import xml.dom.minidom

def imagecompare(imgfile1, imgfile2):
    try:
        import ImageChops, Image
    except ImportError:
        raise Exception, 'Python-Imaging package not installed'
    try:
        diffcount = 0.0
        im1 = Image.open(imgfile1)
        im2 = Image.open(imgfile2)

        imgcompdiff = ImageChops.difference(im1, im2)
        diffboundrect = imgcompdiff.getbbox()
        imgdiffcrop = imgcompdiff.crop(diffboundrect)

        data = imgdiffcrop.getdata()

        seq = []
        for row in data:
            seq += list(row)

        for i in xrange(0, imgdiffcrop.size[0] * imgdiffcrop.size[1] * 3, 3):
            if seq[i] != 0 or seq[i+1] != 0 or seq[i+2] != 0:
                diffcount = diffcount + 1.0
        
        diffImgLen = imgcompdiff.size[0] * imgcompdiff.size[1] * 1.0
        diffpercent = (diffcount * 100) / diffImgLen
        return diffpercent
    except IOError:
        raise Exception, 'Input file does not exist'

# XML Data file parser
class LdtpDataFileParser:
    def __init__(self, filename = None):
        self.ldtpdataxml = []
        if filename:
            try:
                dom = xml.dom.minidom.parse(filename)
                self.ldtpdataxml = dom.getElementsByTagName("data")
                if self.ldtpdataxml == []:
                    ldtp.log('data xml tag not present')
                    if _ldtpDebug and _ldtpDebug == '2':
                        print 'data xml tag not present'
            except xml.parsers.expat.ExpatError, msg:
                ldtp.log('XML Error: ' + str(msg), 'error')
            except IOError:
                ldtp.log('XML \"' + filename + '\" file not found', 'error')
    def setfilename(self, filename):
        self.ldtpdataxml = []
        if filename:
            try:
                dom = xml.dom.minidom.parse(filename)
                self.ldtpdataxml = dom.getElementsByTagName("data")
                if self.ldtpdataxml == []:
                    ldtp.log('data xml tag not present')
                    if _ldtpDebug and _ldtpDebug == '2':
                        print 'data xml tag not present'
            except xml.parsers.expat.ExpatError, msg:
                if _ldtpDebug and _ldtpDebug == '2':
                    print 'XML Error: ' + str(msg)
                ldtp.log('XML Error: ' + str(msg), 'error')
            except IOError:
                if _ldtpDebug and _ldtpDebug == '2':
                    print 'XML \"' + filename + '\" file not found'
                ldtp.log('XML \"' + filename + '\" file not found', 'error')
    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
    def gettagvalue(self, tagname):
        self.taglist = []
        if self.ldtpdataxml == []:
            return self.taglist
        for dataelements in self.ldtpdataxml:
            for data in dataelements.getElementsByTagName(tagname):
                self.taglist.append(self.getText(data.childNodes))
        return self.taglist
