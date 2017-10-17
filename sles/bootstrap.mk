# @copyright@
# @copyright@

bootstrap:
	$(STACKBUILD)/bin/package-install -m 32bit Basis-Devel SDK-C-C++
	$(STACKBUILD)/bin/package-install rpm-build libzip2 apache2 squashfs apache2-devel createrepo

