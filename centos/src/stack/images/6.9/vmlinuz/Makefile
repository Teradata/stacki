# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT		= ../../../../../..

include $(STACKBUILD)/etc/CCRules.mk


build:
	echo "Building vmlinuz"

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	cp vmlinuz $(ROOT)/$(PKGROOT)/vmlinuz-$(VERSION)-$(RELEASE)-$(ARCH)

