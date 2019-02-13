# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


ROLLROOT = ../../../..
include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	# Install discovery-nodes
	mkdir -p $(ROOT)/opt/stack/sbin
	$(INSTALL) -m0555 bin/discover-nodes.py $(ROOT)/opt/stack/sbin/discover-nodes

	# Install pylib
	mkdir -p $(ROOT)/$(PY.STACK)/stack/
	$(INSTALL) -m0644 pylib/*.py $(ROOT)/$(PY.STACK)/stack/

	# Install command
	(					\
		cd command;			\
		find . -type f -name \*.py |	\
		cpio -pudv $(ROOT)/$(PY.STACK)/stack/commands;	\
	)
	
	find $(ROOT)/$(PY.STACK)/stack/commands -name "*.py" | gawk	\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'  

clean::
