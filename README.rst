====
LDTP
====

`LDTP <http://ldtp.freedesktop.org>`_ is the best cross platform GUI testing
tool out there. Why? Because it works on Linux, Windows, OS X, Solairs,
FreeBSD, NetBSD, and Palm Source. Your feedback is much appreciated, please
send an email to `Nagappan <nagappan@gmail.com>`_.

LDTP runs on
============

 - `OpenSUSE <http://www.opensuse.org/>`_
 - `OpenSolaris <http://opensolaris.org/>`_
 - `Ubuntu <http://ubuntu.com/>`_
 - `Debian <http://www.debian.org/>`_
 - `Fedora <http://fedoraproject.org/>`_
 - `FreeBSD <http://www.freebsd.org/>`_

Requirements
============

DE Requirements
---------------
 - GNOME Version - min 2.24
 - Accessibility enabled

Dependencies
------------

 - pyatspi (python-atspi)
 - python-twisted-web
 - python-wnck
 - python-gnome

Optional Dependencies
---------------------

 - Python Imaging Library (http://www.pythonware.com/products/pil/) to compare two images
 - Pystatgrab (http://www.i-scream.org/pystatgrab/) to monitor memory and CPU utilization

Build LDTP on Linux
===================

First checkout ldtp from github and cd into ldtp2.

  $ git clone https://github.com/ldtp/ldtp2.git

  $ cd ldtp2/

Then build and install.

  $ python setup.py build

  $ sudo python setup.py install

Note: If your GNOME version is less than or equal to 2.24, then use LDTPv1 (1.7.x)

Writing tests
=============

It is best to read the documentation, so first cd into the doc directory.

  $ cd ldtp2/doc/

Then you can either read ldtp-tutorial.rst in you favorite text editor or build
a pdf. First install ``rst2pdf``, then run:

  $ rst2pdf ldtp-tutorial.rst

Then open the pdf in your favorite pdf viewer.

You can also refer to the following for more information:

`Writing LDTP test scripts in Python scripting language <http://ldtp.freedesktop.org/wiki/LDTP_test_scripts_in_python>`_
`LDTP API Reference page <http://ldtp.freedesktop.org/user-doc/index.html>`_

Contact LDTP
============

We are in #ldtp on irc.freenode.net and are also available on the `LDTP mailing
list <http://ldtp.freedesktop.org/wiki/Mailing_20list>`_

Contributing
============

So you want to help? Fantastic! If you are looking for ideas on what to work on
ask on the mailing list or ping us in irc, we love meeting new people.

Generally the process is fork https://github.com/ldtp/ldtp2, make your changes, and make a pull request.
