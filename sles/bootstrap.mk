# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

bootstrap:
	$(STACKBUILD)/bin/package-install -m 32bit Basis-Devel SDK-C-C++
	$(STACKBUILD)/bin/package-install rpm-build libzip2 apache2 squashfs apache2-devel createrepo

