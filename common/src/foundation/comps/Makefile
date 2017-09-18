#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= comps.xml
DISTVERSION	= $(shell stack report version)
RPM.ARCH	= noarch

include $(STACKBUILD)/etc/CCRules.mk

build: 

install::
	mkdir -p $(ROOT)/RedHat/base
	install -ma+r comps.xml $(ROOT)/RedHat/base

