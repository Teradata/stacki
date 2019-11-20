# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGLIST = apache2 squashfs apache2-devel createrepo cdrkit-cdrtools-compat
PATLIST = 32bit Basis-Devel

ifeq ($(RELEASE),sles12)
PKGLIST += rpm-build libzip2 libvirt-devel
endif

ifeq ($(RELEASE),sles11)
PKGLIST += libzip1 brp-check-suse
endif

bootstrap:
	../common/src/stack/build/build/bin/package-install -m $(PATLIST)
	../common/src/stack/build/build/bin/package-install $(PKGLIST)

