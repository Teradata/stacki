# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/etc/init.d/
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	$(INSTALL) -m 0755 aws-client-register.py $(ROOT)/$(PKGROOT)/sbin/aws-client-register
	$(INSTALL) -m 0755 aws-server-init.py     $(ROOT)/$(PKGROOT)/sbin/aws-server-init



