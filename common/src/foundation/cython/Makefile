# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= $(ARCHIVENAME)-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk

build: 
	tar -xzf $(ARCHIVENAME)-$(VERSION).tar.gz
	(					\
		cd $(ARCHIVENAME)-$(VERSION);	\
		$(PY.PATH) setup.py build;	\
	)

install::
	(					\
		cd $(ARCHIVENAME)-$(VERSION);	\
		$(PY.PATH) setup.py install	\
			--root=$(ROOT);	\
	)


clean::
	rm -rf $(ARCHIVENAME)-$(VERSION)
