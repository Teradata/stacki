# @Copyright@
# @Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../..
DEPENDS.FILES	= use_the_source.py

include $(STACKBUILD)/etc/CCRules.mk


build:
	echo "Building ... "

install::
	mkdir -p -m 550 $(ROOT)/$(PKGROOT)/bin/
	$(INSTALL) -m 0550 use_the_source.py $(ROOT)/$(PKGROOT)/bin/use_the_source

