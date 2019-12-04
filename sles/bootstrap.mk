# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGLIST = apache2 squashfs apache2-devel
PATLIST = 32bit

ifeq ($(RELEASE),sles15)
PKGLIST += rpm-build libzip5 createrepo_c mkisofs libvirt-devel
PATLIST += devel_basis
endif

ifeq ($(RELEASE),sles12)
PKGLIST += rpm-build libzip2 createrepo cdrkit-cdrtools-compat libvirt-devel
PATLIST += Basis-Devel
endif

ifeq ($(RELEASE),sles11)
PKGLIST += libzip1 brp-check-suse createrepo cdrkit-cdrtools-compat
PATLIST += Basis-Devel
endif

bootstrap:
	../common/src/stack/build/build/bin/package-install -m $(PATLIST)
	../common/src/stack/build/build/bin/package-install $(PKGLIST)

