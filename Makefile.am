## Process this file with automake to produce Makefile.in
## Created by Anjuta

SUBDIRS = src 

sagidocdir = ${prefix}/doc/sagi
sagidoc_DATA = \
	README\
	COPYING\
	AUTHORS\
	ChangeLog\
	INSTALL\
	NEWS


EXTRA_DIST = $(sagidoc_DATA)


# Remove doc directory on uninstall
uninstall-local:
	-rm -r $(sagidocdir)
