# @SI_Copyright@
# Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@

ROLLROOT	= ../../..
EXTRAS.DIRS	= opt usr

include $(STACKBUILD)/etc/CCRules.mk


build:
	../../build-initrd.py --rpms=$(REDHAT.RPMS) --pkgs="$(OVERLAY.PKGS)" \
		--update-pkgs="$(OVERLAY.UPDATE.PKGS)" --build-directory=build
	find $(EXTRAS.DIRS) -type f | cpio -pduv build

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(cd build ; \
		find . | cpio -c -o | gzip -9cv > \
		$(ROOT)/$(PKGROOT)/updates.img ; \
	)

clean::
	rm -rf build
	rm -rf $(OVERLAY.PKGS)

nuke::
	rm -rf default

