# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack/
ROLLROOT	= ../../../..
DEPENDS.DIRS	= bin lib

include $(STACKBUILD)/etc/CCRules.mk


build::

install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	mkdir -p $(ROOT)/$(PKGROOT)/lib
	mkdir -p $(ROOT)/$(PKGROOT)/lib/stacki_default_part/
	$(INSTALL) -m755 bin/*py $(ROOT)/$(PKGROOT)/bin/
	$(INSTALL) -m644 lib/*py $(ROOT)/$(PKGROOT)/lib/
	$(INSTALL) -m644 lib/stacki_default_part/*.py \
		$(ROOT)/$(PKGROOT)/lib/stacki_default_part/

