# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..

include $(STACKBUILD)/etc/CCRules.mk

build:
	tar -xzf wxPython-$(VERSION).tar.gz
	(								\
		cd wxPython-$(VERSION);					\
		$(PY.PATH) ./build.py build 				\
			--gtk3						\
			--destdir=$(PKGROOT);				\
	)

install::
	(								\
		cd wxPython-$(VERSION);					\
		$(PY.PATH) ./build.py install				\
			--gtk3						\
			--destdir=$(ROOT) 				\
			--prefix=$(PKGROOT);				\
	)

clean::
	rm -rf wxPython-$(VERSION)
