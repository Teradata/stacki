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

bootstrap:: install-rpm

build:
	tar -xzf newt-$(VERSION).tar.gz
	( 								\
		cd newt-$(VERSION);					\
		./configure --prefix=$(PKGROOT); 			\
		PATH=/bin:/usr/bin:$(PKGROOT)/bin;			\
		$(MAKE) PYTHONVERS=$(PY.LIB);				\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(								\
		cd newt-$(VERSION);					\
		PATH=/bin:/usr/bin:$(PKGROOT)/bin;			\
		$(MAKE) PYTHONVERS=$(PY.LIB) install DESTDIR=$(ROOT);	\
	)

clean::
	rm -rf newt-$(VERSION)
