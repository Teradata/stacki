# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= gen_random_pw.py stack-console.py		

include $(ROCKSBUILD)/etc/CCRules.mk

ROOTONLY	= gen_random_pw
ANYONE		= stack-console
SCRIPTS		= $(ANYONE) $(ROOTONLY)

build:

install:: $(SCRIPTS)
	mkdir -p $(ROOT)/$(PKGROOT)/sbin/
	$(INSTALL) -m0555 $(ANYONE) $(ROOT)/$(PKGROOT)/sbin/
	$(INSTALL) -m0500 $(ROOTONLY) $(ROOT)/$(PKGROOT)/sbin/

clean::
	rm -f $(SCRIPTS)

