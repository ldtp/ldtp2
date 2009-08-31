ldtpd_DATA = \
	server_exception.py \
	keypress_actions.py \
	generic.py \
	xmlrpc_daemon.py \
	waiters.py \
	mouse.py \
	value.py \
	text.py \
	constants.py \
	log.py \
	core.py \
	menu.py \
	sequence_step.py \
	utils.py \
	page_tab_list.py \
	table.py \
	combo_box.py \
	__init__.py

pyc_DATA = $(ldtpd_DATA:.py=.pyc)
pycdir = $(ldtpddir)

%.pyc: %.py
	$(PYTHON_CMD) -c "import py_compile; py_compile.compile ('$<', '$@')"

EXTRA_DIST =		\
	$(ldtpd_DATA)

CLEANFILES =	\
	$(pyc_DATA)

MAINTAINERCLEANFILES =	\
	Makefile.in
