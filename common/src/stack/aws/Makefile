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
	$(INSTALL) -m 0755 ssh-aws.init	$(ROOT)/etc/init.d/ssh-aws
	$(INSTALL) -m 0755 register.py  $(ROOT)/$(PKGROOT)/sbin/register



