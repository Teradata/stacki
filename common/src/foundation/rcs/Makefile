# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= rcs-$(VERSION).tar.gz
DEPENDS.DIRS	= patch-files

include $(STACKBUILD)/etc/CCRules.mk


build:
	gunzip -c rcs-$(VERSION).tar.gz | $(TAR) -xf -
	(cd patch-files && find . -type f | grep -v CVS | cpio -pduv ../)
	( 								\
		cd rcs-$(VERSION);					\
		./configure --prefix=$(PKGROOT);			\
		$(MAKE);						\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(								\
		cd rcs-$(VERSION);					\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT) install;		\
	)

clean::
	rm -rf rcs-$(VERSION)
