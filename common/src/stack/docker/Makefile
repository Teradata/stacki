# @copyright@
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/etc/systemd/system
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	$(INSTALL) -m 0664 docker-barnacle.service $(ROOT)/etc/systemd/system/stack-docker-barnacle.service
	$(INSTALL) -m 0755 docker-barnacle.sh      $(ROOT)/$(PKGROOT)/sbin/docker-barnacle



