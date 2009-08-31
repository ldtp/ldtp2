ldtputils_DATA = \
	__init__.py

pyc_DATA = $(ldtputils_DATA:.py=.pyc)
pycdir = $(ldtputilsdir)

%.pyc: %.py
	$(PYTHON_CMD) -c "import py_compile; py_compile.compile ('$<', '$@')"

EXTRA_DIST =		\
	$(ldtputils_DATA)

CLEANFILES =	\
	$(pyc_DATA)

MAINTAINERCLEANFILES =	\
	Makefile.in
