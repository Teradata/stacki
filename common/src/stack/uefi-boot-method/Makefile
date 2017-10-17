# @copyright@
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

