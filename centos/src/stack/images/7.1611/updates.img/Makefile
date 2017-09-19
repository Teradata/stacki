# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../../..
EXTRAS.DIRS	= opt usr

include $(STACKBUILD)/etc/CCRules.mk


build:
	../../build-initrd.py --rpms=$(REDHAT.RPMS) --pkgs="$(OVERLAY.PKGS)" \
		--update-pkgs="$(OVERLAY.UPDATE.PKGS)" --build-directory=build
	find $(EXTRAS.DIRS) -type f | cpio -pduv build
	(cd build ; \
		mksquashfs * ../updates.img \
			-keep-as-directory ; \
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	$(INSTALL) updates.img $(ROOT)/$(PKGROOT)

clean::
	rm -rf build
	rm -rf $(OVERLAY.PKGS)
	rm -rf updates.img

nuke::
	rm -rf default

