## Process this file with automake to produce Makefile.in
## Created by Anjuta


uidir = $(datadir)/sagi/ui
ui_DATA = sagi.ui \
	sagi.png


## The main script
bin_SCRIPTS = sagi.py \
	aria.py

## Directory where .class files will be installed
sagidir = $(pythondir)/sagi


sagi_PYTHON = \
	sagi.py


EXTRA_DIST = $(ui_DATA)


# Remove ui directory on uninstall
uninstall-local:

	-rm -r $(uidir)

	-rm -r $(datadir)/sagi
