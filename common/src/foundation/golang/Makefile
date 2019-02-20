# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

ROLLROOT = ../../../..
PKGROOT=/opt/stack
DEPENDS.FILES=$(ARCHIVENAME)$(VERSION).$(PLATFORM).tar.gz

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)$(PKGROOT)
	tar -C $(ROOT)$(PKGROOT) -xzf $(ARCHIVENAME)$(VERSION).$(PLATFORM).tar.gz

clean::
	rm -rf $(ARCHIVENAME)$(VERSION).$(PLATFORM)
