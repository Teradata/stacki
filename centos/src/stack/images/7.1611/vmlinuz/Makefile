# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../../..

include $(STACKBUILD)/etc/CCRules.mk


build:
	echo "Building vmlinuz"

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	cp vmlinuz $(ROOT)/$(PKGROOT)/vmlinuz-$(VERSION)-$(RELEASE)-$(ARCH)

