# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.DIRS	= files
DEPENDS.RPMS	= iperf3

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	$(INSTALL) -m0755 files/iperf3.py $(ROOT)/$(PKGROOT)/sbin/iperf3.py
	mkdir -p $(ROOT)/$(INIT_SCRIPTS_DIR)
	mkdir -p $(ROOT)/usr/lib/systemd/system
	$(INSTALL) -m0755 files/iperf3.init $(ROOT)/$(INIT_SCRIPTS_DIR)/iperf3
	$(INSTALL) -m0755 files/iperf3.service $(ROOT)/usr/lib/systemd/system/iperf3.service

