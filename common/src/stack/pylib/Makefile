# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


PYLIB		= $(wildcard *.py)
PYAPI		= $(wildcard api/*.py)
PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.DIRS	= stack

include $(STACKBUILD)/etc/CCRules.mk

dump-info::
	@echo "STACK_RELEASE   = $(STACK_RELEASE)"
	@echo "STACK_VERSION   = $(STACK_VERSION)"

bootstrap: install-rpm

build:

install:: build
	mkdir -p $(ROOT)/$(PY.STACK)/stack
	(								\
		cd stack;						\
		find . -name "*.py" | 					\
			cpio -pduv $(ROOT)/$(PY.STACK)/stack;		\
		rm $(ROOT)/$(PY.STACK)/stack/__init__.py;		\
	)
	@echo "version = \"$(STACK_VERSION)\"" >> \
		$(ROOT)/$(PY.STACK)/stack/__init__.py
	@echo "release = \"$(STACK_RELEASE)\"" >> \
		$(ROOT)/$(PY.STACK)/stack/__init__.py

clean::
	find stack -name *.pyc -exec rm -f {} \;


