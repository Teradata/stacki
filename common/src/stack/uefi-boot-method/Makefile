# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= uefi_boot_method.py uefi-boot-method.service

include $(STACKBUILD)/etc/CCRules.mk


build:


install::
	mkdir -p $(ROOT)/opt/stack/bin/ $(ROOT)/lib/systemd/system/
	$(INSTALL) -m 0755 uefi_boot_method.py $(ROOT)/opt/stack/bin/
	$(INSTALL) -m 0644 uefi-boot-method.service $(ROOT)/lib/systemd/system/
	mkdir -p $(ROOT)/etc/init.d/
	$(INSTALL) -m 0755 uefi-boot-method.init $(ROOT)/etc/init.d/uefi-boot-method

