# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
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
