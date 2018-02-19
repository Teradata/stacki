# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.DIRS	= stack
DEPENDS.FILES	= stack.py
PY.TEST.FLAGS   = -s

include $(STACKBUILD)/etc/CCRules.mk

bootstrap: install-rpm

doc:
	$(STACKBUILD)/src/pallet/etc/doc/genrcldocs stacki markdoc

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	mkdir -p $(ROOT)/$(PY.STACK)/stack
	$(INSTALL) -m0555 stack.py $(ROOT)/$(PKGROOT)/bin/stack
	(								\
		cd stack;						\
		find . -name "*.py" | 					\
			cpio -pduv $(ROOT)/$(PY.STACK)/stack;		\
		rm $(ROOT)/$(PY.STACK)/stack/__init__.py;		\
	)
	find $(ROOT)/$(PY.STACK)/stack/ -name "*.py" | gawk		\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'  
	find $(ROOT) -type d -exec chmod a+rx {} \;

clean::
	find stack -name *.pyc -exec rm -f {} \;
	rm -rf cli
