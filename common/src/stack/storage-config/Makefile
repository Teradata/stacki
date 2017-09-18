#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

PKGROOT		= /opt/stack/
ROLLROOT	= ../../..
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

