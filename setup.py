#!/usr/bin/env python

from distutils.core import setup

setup(name='LDTPv2',
      version='0.1',
      description='Linux Desktop Testing Project Version 2',
      maintainer='Nagappan Alagappan',
      maintainer_email='nagappan@gmail.com',
      url='http://ldtp.freesktop.org',
      packages=['ldtp', 'ldtpd', 'ooldtp'],
      scripts=['ldtpd.sh']
      )
