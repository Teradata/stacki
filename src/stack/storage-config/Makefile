#
# @SI_Copyright@
# @SI_Copyright@
#

PKGROOT		= /opt/stack/
ROLLROOT	= ../../..
DEPENDS.DIRS	= bin lib

include $(STACKBUILD)/etc/CCRules.mk


build::

install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	mkdir -p $(ROOT)/$(PKGROOT)/lib
	$(INSTALL) -m755 bin/*py $(ROOT)/$(PKGROOT)/bin/
	$(INSTALL) -m644 lib/*py $(ROOT)/$(PKGROOT)/lib/

