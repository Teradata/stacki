# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= Python-$(VERSION).tgz

include $(STACKBUILD)/etc/CCRules.mk

BOOTSTRAP        = readline-devel xz-devel
BOOTSTRAP.redhat = openssl-devel bzip2-libs bzip2-devel
BOOTSTRAP.sles   = libopenssl-devel bzip2 libzip2 

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
