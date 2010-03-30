#!/usr/bin/env python

from distutils.core import setup

setup(name='ldtp',
      version='2.0.5',
      description='Linux Desktop Testing Project Version 2',
      maintainer='Nagappan Alagappan',
      maintainer_email='nagappan@gmail.com',
      url='http://ldtp.freesktop.org',
      license="GNU Lesser General Public License (LGPL)",
      packages=['ldtp', 'ldtpd', 'ooldtp', 'ldtputils'],
      long_description='Linux Desktop Testing Project is aimed at producing ' \
          'high quality test automation framework and cutting-edge tools that ' \
          'can be used to test GNU/Linux Desktop and improve it. It uses the ' \
          'Accessibility libraries to poke through the applications user ' \
          'interface. LDTP is a Linux / Unix GUI application testing tool. ' \
          'It runs on Linux / Solaris / FreeBSD / Embedded environment (Palm Source).',
      scripts=['scripts/ldtp'],
      classifiers=[
        'Development Status :: 5 - Production',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License (LGPL)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Solaris',
        'Operating System :: POSIX :: FreeBSD',
        'Programming Language :: Python',
        'Topic :: Desktop Environment',
        ]
      )
