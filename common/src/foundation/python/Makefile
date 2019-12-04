# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= Python-$(VERSION).tgz

include $(STACKBUILD)/etc/CCRules.mk

BOOTSTRAP        = readline-devel xz-devel
BOOTSTRAP.redhat = openssl-devel bzip2-libs bzip2-devel libffi-devel sqlite-devel
BOOTSTRAP.sles11 = libffi-devel
BOOTSTRAP.sles12 = libffi48-devel
BOOTSTRAP.sles15 = libffi-devel
BOOTSTRAP.sles   = libopenssl-devel bzip2 libzip2 libbz2-devel sqlite3-devel $(BOOTSTRAP.$(RELEASE))

bootstrap:
	$(STACKBUILD)/bin/package-install $(BOOTSTRAP) $(BOOTSTRAP.$(OS))
	$(MAKE) install-rpm
	$(PY.PATH) -mensurepip


build:
	tar -xzf Python-$(VERSION).tgz
	( 								\
		cd Python-$(VERSION);					\
		./configure --prefix=$(PKGROOT)				\
			--enable-shared					\
			--without-ensurepip				\
			--without-pymalloc;				\
		$(MAKE);						\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(								\
		cd Python-$(VERSION);					\
		$(MAKE) install DESTDIR=$(ROOT) ;			\
	)
	# Lay down the ldconf file in the right place.
	# %post and %postun will run ldconfig to apply it.
	mkdir -p $(ROOT)/etc/ld.so.conf.d
	cp stacki-python.conf $(ROOT)/etc/ld.so.conf.d/

clean::
	rm -rf Python-$(VERSION)
