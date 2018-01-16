# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= $(wildcard *.py)

include $(STACKBUILD)/etc/CCRules.mk

build:	

install::
	mkdir -p $(ROOT)/etc/systemd/system
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	mkdir -p $(ROOT)/export/stack/sbin
	$(INSTALL) -m 0664 aws-server-init.service  $(ROOT)/etc/systemd/system/stack-aws-server-init.service
	$(INSTALL) -m 0755 aws-server-init.py       $(ROOT)/$(PKGROOT)/sbin/aws-server-init
	$(INSTALL) -m 0755 register.py              $(ROOT)/export/stack/sbin/register.cgi




