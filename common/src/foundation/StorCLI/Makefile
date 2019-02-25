# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
RPMFILE		= $(NAME)-$(VERSION)-1.noarch.rpm
DEPENDS.FILES	= $(RPMFILE)

include $(STACKBUILD)/etc/CCRules.mk

build:
	mkdir $(CURDIR)/tmp/
	rpm -i --force --noscripts --badreloc \
		--relocate /=$(CURDIR)/tmp/ $(RPMFILE)

install::
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	$(INSTALL) -m755 \
		$(CURDIR)/tmp/opt/MegaRAID/storcli/storcli64 \
		$(ROOT)/$(PKGROOT)/sbin/storcli

clean::
	rm -rf tmp
