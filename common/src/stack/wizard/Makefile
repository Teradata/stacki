# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.DIRS	= gui

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	cp gui/* $(ROOT)/$(PKGROOT)/bin

