ldtp_DATA = \
	log.py \
	state.py	\
	client_exception.py \
	client.py \
	__init__.py

pyc_DATA = $(ldtp_DATA:.py=.pyc)
pycdir = $(ldtpdir)

%.pyc: %.py
	$(PYTHON_CMD) -c "import py_compile; py_compile.compile ('$<', '$@')"

EXTRA_DIST =		\
	$(ldtp_DATA)

CLEANFILES =	\
	$(pyc_DATA)

MAINTAINERCLEANFILES =	\
	Makefile.in
