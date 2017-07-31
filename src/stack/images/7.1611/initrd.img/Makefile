# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

ROLLROOT		= ../../../../..
DEPENDS.DIRS		= images dracut

include $(STACKBUILD)/etc/CCRules.mk


build:
	mkdir build
	(cd build ; xzcat ../initrd.img | cpio -idu) 
	../../build-initrd.py --rpms=$(REDHAT.RPMS) --pkgs="$(OVERLAY.PKGS)" \
		--update-pkgs="$(OVERLAY.UPDATE.PKGS)" --build-directory=build
	cp -r dracut build/usr/lib/

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(cd build ; \
		find . | cpio --quiet -c -o | xz -9 --format=lzma > \
			$(ROOT)/$(PKGROOT)/initrd.img-$(VERSION)-$(RELEASE)-$(ARCH) \
	)

clean::
	rm -rf build
	rm -rf $(OVERLAY.PKGS) $(OVERLAY.UPDATE.PKGS)

nuke::
	rm -rf default

