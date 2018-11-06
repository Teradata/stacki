# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../../..
FILES		= isolinux.bin isolinux.cfg menu.cfg splash.png \
			vesamenu.c32 chain.c32

include $(STACKBUILD)/etc/CCRules.mk


build:
	echo "Building isolinux"
	cat menu-header > menu.cfg
	echo "menu title stacki $(VERSION) ($(RELEASE))" >> menu.cfg
	cat menu-footer >> menu.cfg

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	cp $(FILES) $(ROOT)/$(PKGROOT)

