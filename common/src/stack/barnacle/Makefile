# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= $(wildcard *.sh) $(wildcard *.service)

include $(STACKBUILD)/etc/CCRules.mk

build:	

install::
	mkdir -p $(ROOT)/etc/systemd/system
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	mkdir -p $(ROOT)/export/stack/sbin
	$(INSTALL) -m 0664 aws-barnacle.service       $(ROOT)/etc/systemd/system/stack-aws-barnacle.service
	$(INSTALL) -m 0755 aws-barnacle.sh            $(ROOT)/$(PKGROOT)/sbin/aws-barnacle
	$(INSTALL) -m 0755 aws-barnacle-prep-image.sh $(ROOT)/$(PKGROOT)/sbin/aws-barnacle-prep-image




