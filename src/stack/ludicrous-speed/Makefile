# @SI_Copyright@
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT 	= ../../..
DEPENDS.FILES	= ludicrous-server.py ludicrous-client.py ludicrous-client.service

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin $(ROOT)/lib/systemd/system
	$(INSTALL) -m 0755 ludicrous-server.py $(ROOT)/$(PKGROOT)/bin
	$(INSTALL) -m 0755 ludicrous-client.py $(ROOT)/$(PKGROOT)/bin
	$(INSTALL) -m 0644 ludicrous-client.service $(ROOT)/lib/systemd/system/
