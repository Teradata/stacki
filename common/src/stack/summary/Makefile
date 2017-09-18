# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.DIRS	= stack

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PY.STACK)/stack
	(								\
		cd stack;						\
		find . -name "*.py" | 					\
			cpio -pduv $(ROOT)/$(PY.STACK)/stack;		\
	)
	find $(ROOT)/$(PY.STACK)/stack/ -name "*.py" | gawk		\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'  

clean::
	find stack -name *.pyc -exec rm -f {} \;
