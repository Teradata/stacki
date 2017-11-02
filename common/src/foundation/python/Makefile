# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= Python-$(VERSION).tgz

include $(STACKBUILD)/etc/CCRules.mk

BOOTSTRAP        = readline-devel
BOOTSTRAP.redhat = openssl-devel bz2-libs bz2-devel xz-devel
BOOTSTRAP.sles   =

bootstrap:
	$(STACKBUILD)/bin/package-install $(BOOTSTRAP) $(BOOTSTRAP.$(OS))
	$(MAKE) install-rpm
	echo $(PKGROOT)/lib > /etc/ld.so.conf.d/stacki-python.conf
	ldconfig
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

clean::
	rm -rf Python-$(VERSION)
