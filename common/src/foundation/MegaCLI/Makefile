# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
RPMFILE		= MegaCli-$(VERSION)-1.noarch.rpm
DEPENDS.FILES	= $(RPMFILE)

include $(STACKBUILD)/etc/CCRules.mk
ifeq ($(OS),debian)
build:
	fpm --input-type rpm --output-type tar --name $(NAME) $(RPMFILE) 
	mkdir $(CURDIR)/tmp/
	(cd $(CURDIR)/tmp; tar -xf ../$(NAME).tar)

clean::
	rm -f $(NAME).tar
else
build:
	mkdir $(CURDIR)/tmp/
	rpm -i --force --noscripts --badreloc \
		--relocate /=$(CURDIR)/tmp/ $(RPMFILE)
endif

install::
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	mkdir -p $(ROOT)/$(PKGROOT)/lib
	$(INSTALL) -m755 \
		$(CURDIR)/tmp/opt/MegaRAID/MegaCli/MegaCli64 \
		$(ROOT)/$(PKGROOT)/sbin/MegaCli
	$(INSTALL) -m0444 \
		$(CURDIR)/tmp/opt/MegaRAID/MegaCli/libstorelibir-2.so.13.05-0 \
		$(ROOT)/$(PKGROOT)/lib/libstorelibir-2.so.13.05-0

clean::
	rm -rf tmp
