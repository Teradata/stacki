# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.DIRS	= resolvers schema pylib

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/usr/lib/systemd/system
	mkdir -p $(ROOT)/$(PY.STACK)/stack/graph_ql/resolvers
	mkdir -p $(ROOT)/$(PY.STACK)/stack/graph_ql/schema

	$(INSTALL) -m 0644 $(wildcard resolvers/*.py)	$(ROOT)/$(PY.STACK)/stack/graph_ql/resolvers/
	$(INSTALL) -m 0644 $(wildcard schema/*.graphql)	$(ROOT)/$(PY.STACK)/stack/graph_ql/schema/
	$(INSTALL) -m 0644 $(wildcard pylib/graph_ql/*.py)	$(ROOT)/$(PY.STACK)/stack/graph_ql/

	$(INSTALL) -m 0644 graphql-server.service $(ROOT)/usr/lib/systemd/system

	# Install command
	(					\
		cd command;			\
		find . -type f -name \*.py |	\
		cpio -pudv $(ROOT)/$(PY.STACK)/stack/commands;	\
	)
	
	find $(ROOT)/$(PY.STACK)/stack/commands -name "*.py" | gawk	\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'

clean::