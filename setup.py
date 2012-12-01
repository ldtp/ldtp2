#!/usr/bin/env python
"""
LDTP v2 Core.

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

from distutils.core import setup

setup(name="ldtp",
      version="3.0.0",
      description="Linux Desktop Testing Project Version 2",
      maintainer="Nagappan Alagappan",
      maintainer_email="nagappan@gmail.com",
      url="http://ldtp.freesktop.org",
      license="GNU Lesser General Public License (LGPL)",
      packages=["ldtp", "ldtpd", "ooldtp", "ldtputils"],
      long_description="Linux Desktop Testing Project is aimed at producing " \
          "high quality cross platform GUI test automation framework and cutting-edge tools that " \
          "can be used to test GNU/Linux/Windows/Mac Desktop and improve it. It uses the " \
          "Accessibility libraries to poke through the applications user " \
          "interface. LDTP is a Linux / Unix GUI application testing tool. " \
          "It runs on Linux / Windows / Mac OSX / Solaris / FreeBSD / Embedded environment (Palm Source).",
      scripts=["scripts/ldtp"],
      classifiers=[
        "Development Status :: 5 - Production",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License (LGPL)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: Solaris",
        "Operating System :: POSIX :: FreeBSD",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Topic :: Desktop Environment",
        ],
      )
