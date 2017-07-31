# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

PKGROOT		= /opt/lighttpd
ROLLROOT	= ../../..
DEPENDS.FILES	= $(NAME)-$(VERSION).tar.gz
DEPENDS.DIRS	= cgi conf

include $(STACKBUILD)/etc/CCRules.mk

bootstrap:
	yum install -y pcre-devel

build:
	tar zvfx $(NAME)-$(VERSION).tar.gz
	(								\
		cd $(NAME)-$(VERSION) ;					\
		./configure --prefix=$(PKGROOT) ;			\
		$(MAKE) ; 						\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(								\
		cd $(NAME)-$(VERSION) ;					\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT) install;		\
	)
	mkdir -p $(ROOT)/$(PKGROOT)/conf
	cp conf/lighttpd.conf $(ROOT)/$(PKGROOT)/conf
	mkdir -p $(ROOT)/$(PKGROOT)/cgi
	cp cgi/index.cgi $(ROOT)/$(PKGROOT)/cgi

clean::
	rm -rf $(NAME)-$(VERSION)

