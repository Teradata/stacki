# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= Python-$(VERSION).tgz

include $(STACKBUILD)/etc/CCRules.mk

bootstrap-redhat::
	yum install -y openssl-devel readline-devel
	echo $(PKGROOT)/lib > /etc/ld.so.conf.d/stacki-python.conf


bootstrap:: install-rpm
	ldconfig


build:
	tar -xzf Python-$(VERSION).tgz
	-cd patch-files && find . -type f | grep -v CVS | cpio -pduv ../
	( 								\
		cd Python-$(VERSION);					\
		./configure --prefix=$(PKGROOT) 			\
			--enable-shared					\
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
