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

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= gd-$(VERSION).tar.gz
DEPENDS.DIRS	= patch-files

include $(STACKBUILD)/etc/CCRules.mk


build:
	gunzip -c gd-$(VERSION).tar.gz | $(TAR) -xf -
	(cd patch-files && find . -type f | grep -v CVS | cpio -pduv ../)
	( 								\
		cd gd-$(VERSION);					\
		./configure --prefix=$(PKGROOT);			\
		$(MAKE);							\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(								\
		cd gd-$(VERSION);					\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT) install;			\
	)

clean::
	rm -rf gd-$(VERSION)
