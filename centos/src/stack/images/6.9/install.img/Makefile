# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT		= ../../../../..

include $(STACKBUILD)/etc/CCRules.mk

install.img:
	cat $@-* > $@

build: install.img
	mkdir mnt
	mount -o loop -t squashfs install.img mnt
	mkdir build
	(cd build ; cp -r ../mnt/* .)
	umount mnt
	../../build-initrd.py --rpms=$(REDHAT.RPMS) --pkgs="$(OVERLAY.PKGS)" \
		--update-pkgs="$(OVERLAY.UPDATE.PKGS)" --build-directory=build
	(cd patch-files ; find . -type f | cpio -pduv ../build/)


install::
	mkdir -p $(ROOT)/$(PKGROOT)
	rm -f $(ROOT)/$(PKGROOT)/install.img
	(cd build ; \
		mksquashfs * $(ROOT)/$(PKGROOT)/install.img \
			-keep-as-directory ; \
	)


clean::
	rm -f install.img
	rm -rf mnt
	rm -rf build default
	rm -rf $(OVERLAY.PKGS) $(OVERLAY.UPDATE.PKGS)
