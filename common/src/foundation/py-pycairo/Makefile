# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
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
DEPENDS.FILES	= pycairo-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk


build:
	gunzip -c pycairo-$(VERSION).tar.gz | $(TAR) -xf -
	(								\
		cd pycairo-$(VERSION);				\
		PATH=/opt/stack/bin:$$PATH				\
			./configure --prefix=$(PKGROOT);		\
		$(MAKE);						\
	)

install::
	(								\
		cd pycairo-$(VERSION);				\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT) install;		\
	)


clean::
	rm -rf pycairo-$(VERSION)

