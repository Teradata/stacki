# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

PKGROOT		= /usr
ROLLROOT	= ../../..
DEPENDS.FILES	= $(NAME)-$(VERSION).tar.gz
RPM.EXTRAS	= "AutoReq: 0"
include $(STACKBUILD)/etc/CCRules.mk

bootstrap: install-rpm

build:
	$(TAR) -xzf $(NAME)-$(VERSION).tar.gz
	( 				\
		cd $(NAME)-$(VERSION);	\
		./configure --prefix=$(PKGROOT); \
		$(MAKE) all;	\
		$(MAKE) man;	\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(				\
		cd $(NAME)-$(VERSION);	\
		$(MAKE) DESTDIR=$(ROOT)	\
			install;	\
		$(MAKE) DESTDIR=$(ROOT)	\
			install-man;	\
	)
	find $(ROOT)/$(PKGROOT)/share/man/man1/ -type f -exec gzip -f {} \;
	find $(ROOT)/$(PKGROOT)/share/man/man3/ -type f -exec gzip -f {} \;
	find $(ROOT)/$(PKGROOT)/share/man/man5/ -type f -exec gzip -f {} \;
	find $(ROOT)/$(PKGROOT)/share/man/man7/ -type f -exec gzip -f {} \;

clean::
	rm -rf $(NAME)-$(VERSION)
