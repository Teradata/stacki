# @copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= fio-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk

build:
	gunzip -c fio-$(VERSION).tar.gz | $(TAR) -xf -
	(				\
		cd fio-$(VERSION);	\
		./configure;		\
		$(MAKE) ;		\
	)
install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(				\
		cd fio-$(VERSION);	\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT) install; \
	)
	mkdir -p $(ROOT)/$(PY.STACK)/salt/modules
	$(INSTALL) -m0644 extras/fio.py $(ROOT)/$(PY.STACK)/salt/modules/fio.py

clean::
	rm -rf fio-$(VERSION)
