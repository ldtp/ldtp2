from ldtp import imagecapture

def imagecompare (imgfile1, imgfile2):
    print 'compare', imgfile1, imgfile2
    try:
        import ImageChops, Image
    except ImportError:
        raise Exception, 'Python-Imaging package not installed'
    try:
        diffcount = 0.0
        im1 = Image.open (imgfile1)
        im2 = Image.open (imgfile2)

        imgcompdiff = ImageChops.difference (im1, im2)
        diffboundrect = imgcompdiff.getbbox ()
        imgdiffcrop = imgcompdiff.crop (diffboundrect)

        print 'foo?'
        data = imgdiffcrop.getdata()

        print data
        seq = []
        for row in data:
            seq += list(row)

        for i in xrange (0, imgdiffcrop.size[0] * imgdiffcrop.size[1] * 3, 3):
            if seq[i] != 0 or seq[i+1] != 0 or seq[i+2] != 0:
                diffcount = diffcount + 1.0
        
        diffImgLen = imgcompdiff.size[0] * imgcompdiff.size[1] * 1.0
        diffpercent = (diffcount * 100) / diffImgLen
        return diffpercent
    except IOError:
        raise Exception, 'Input file does not exist'
