# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.DIRS	= files

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	$(INSTALL) -m0755 files/iperf3.py $(ROOT)/$(PKGROOT)/sbin/iperf3.py
	mkdir -p $(ROOT)/$(INIT_SCRIPTS_DIR)
	mkdir -p $(ROOT)/usr/lib/systemd/system
	$(INSTALL) -m0755 files/iperf3.init $(ROOT)/$(INIT_SCRIPTS_DIR)/iperf3
	$(INSTALL) -m0755 files/iperf3.service $(ROOT)/usr/lib/systemd/system/iperf3.service

