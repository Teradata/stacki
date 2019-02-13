# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
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



