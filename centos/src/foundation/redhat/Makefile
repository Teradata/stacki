# @copyright@
# @SI_Copyrighr@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#


PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= getrpms.py

include $(STACKBUILD)/etc/CCRules.mk

RPMS = rpm-python

build: 

install::
	mkdir -p $(ROOT)/$(PKGROOT)/redhat
	./getrpms.py $(ROOT)/$(PKGROOT)/redhat $(RPMS)
	rm -rf $(ROOT)/$(PKGROOT)/redhat/var

