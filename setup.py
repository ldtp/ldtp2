#!/usr/bin/env python

from distutils.core import setup

setup(name='ldtp',
      version='2.0.1',
      description='Linux Desktop Testing Project Version 2',
      maintainer='Nagappan Alagappan',
      maintainer_email='nagappan@gmail.com',
      url='http://ldtp.freesktop.org',
      packages=['ldtp', 'ldtpd', 'ooldtp', 'ldtputils'],
      scripts=['ldtpd.sh']
      )
