# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= newt-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk

bootstrap-redhat::
	yum install -y slang-devel popt-devel

build:
	tar -xzf newt-$(VERSION).tar.gz
	-cd patch-files && find . -type f | grep -v CVS | cpio -pduv ../
	( 								\
		cd newt-$(VERSION);					\
		./configure --prefix=$(PKGROOT); 			\
		$(MAKE);						\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(								\
		cd newt-$(VERSION);					\
		$(MAKE) install DESTDIR=$(ROOT);			\
	)

clean::
	rm -rf newt-$(VERSION)
