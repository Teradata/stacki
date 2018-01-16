# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT		= ../../../../../..

include $(STACKBUILD)/etc/CCRules.mk


build:
	make -C anaconda build
	mkdir build
	(cd build ; \
		lzcat ../initrd.img | cpio -idu ; \
		cp ../anaconda/loader sbin/ ; \
		chmod a+x sbin/loader ; \
		cp ../anaconda/init sbin/ ; \
		chmod a+x sbin/init)
	../../build-initrd.py --rpms=$(REDHAT.RPMS) --pkgs="$(OVERLAY.PKGS)" \
		--update-pkgs="$(OVERLAY.UPDATE.PKGS)" --build-directory=build

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(cd build ; \
		find . | cpio --quiet -c -o | xz -9 --format=lzma > \
			$(ROOT)/$(PKGROOT)/initrd.img-$(VERSION)-$(RELEASE)-$(ARCH) \
	)

clean::
	make -C anaconda clean
	rm -rf build
	rm -rf $(OVERLAY.PKGS) $(OVERLAY.UPDATE.PKGS)

nuke::
	rm -rf default

