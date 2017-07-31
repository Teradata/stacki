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

PKGROOT		= /
ROLLROOT	= ../../..
DEPENDS.DIRS	= init.d profile.d cgi

include $(ROCKSBUILD)/etc/CCRules.mk

build::

install::
	mkdir -p $(ROOT)/etc/profile.d/
	mkdir -p $(ROOT)/etc/init.d/
	mkdir -p $(ROOT)/export/stack/pallets
	$(INSTALL) -m755 profile.d/ssh-key.csh $(ROOT)/etc/profile.d/
	$(INSTALL) -m755 profile.d/ssh-key.sh $(ROOT)/etc/profile.d/
	$(INSTALL) -m755 init.d/stack-num-cpus $(ROOT)/etc/init.d/
	$(INSTALL) -m755 cgi/index.cgi $(ROOT)/export/stack/pallets/index.cgi
	$(INSTALL) -m755 cgi/pallets.cgi $(ROOT)/export/stack/pallets/pallets.cgi
