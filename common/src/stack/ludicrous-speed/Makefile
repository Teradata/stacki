# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT 	= ../../../..
DEPENDS.FILES	= ludicrous-server.py ludicrous-client.py ludicrous-client.service ludicrous-server.service directory.html

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin/templates $(ROOT)/lib/systemd/system 
	$(INSTALL) -m 0755 ludicrous-server.py $(ROOT)/$(PKGROOT)/bin
	$(INSTALL) -m 0755 ludicrous-client.py $(ROOT)/$(PKGROOT)/bin
	$(INSTALL) -m 0755 directory.html $(ROOT)/$(PKGROOT)/bin/templates/
	$(INSTALL) -m 0644 ludicrous-client.service $(ROOT)/lib/systemd/system/
	$(INSTALL) -m 0644 ludicrous-server.service $(ROOT)/lib/systemd/system/
