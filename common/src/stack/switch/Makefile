# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


ROLLROOT = ../../../..
include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	# Install pylib
	mkdir -p $(ROOT)/$(PY.STACK)/stack/

	(								\
		cd pylib;						\
		find . -name "*.py" |					\
			cpio -pduv $(ROOT)/$(PY.STACK)/stack;		\
	)

	# Install command
	(					\
		cd command;			\
		find . -type f -name \*.py |	\
		cpio -pudv $(ROOT)/$(PY.STACK)/stack/commands;	\
	)
	
	find $(ROOT)/$(PY.STACK)/stack/commands -name "*.py" | gawk	\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'  

clean::

