ooldtp_DATA = \
	_context.py	\
	__init__.py

pyc_DATA = $(ooldtp_DATA:.py=.pyc)
pycdir = $(ooldtpdir)

%.pyc: %.py
	$(PYTHON_CMD) -c "import py_compile; py_compile.compile ('$<', '$@')"

EXTRA_DIST =		\
	$(ooldtp_DATA)

CLEANFILES =	\
	$(pyc_DATA)

MAINTAINERCLEANFILES =	\
	Makefile.in
