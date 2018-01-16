# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= stream.tar.gz
DEPENDS.DIRS	= extras
include $(STACKBUILD)/etc/CCRules.mk

build:
	$(TAR) xf stream.tar.gz
	(			\
		cd stream;	\
		$(MAKE) $(BINARY); \
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	mkdir -p $(ROOT)/$(PY.STACK)/salt/modules
	$(INSTALL) -m0755 stream/$(BINARY) $(ROOT)/$(PKGROOT)/bin
	$(INSTALL) -m0644 extras/stream.py $(ROOT)/$(PY.STACK)/salt/modules/stream.py

clean::
	rm -rf stream

