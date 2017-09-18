# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= $(wildcard *.py)
DEPENDS.DIRS	= utils


include $(STACKBUILD)/etc/CCRules.mk


build:	$(SCRIPTS) $(RCFILES)
	$(MAKE) -C utils

install::
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	$(INSTALL) -m 4555 utils/read-ssh-private-key $(ROOT)/$(PKGROOT)/sbin/
	$(INSTALL) -m 4555 utils/read-411-shared-key $(ROOT)/$(PKGROOT)/sbin/

	mkdir -p $(ROOT)/export/stack/sbin/profile
	$(INSTALL) -m 0755 profile.py  $(ROOT)/export/stack/sbin/profile.cgi
	$(INSTALL) -m 0755 __init__.py $(ROOT)/export/stack/sbin/profile/
	$(INSTALL) -m 0755 redhat.py  $(ROOT)/export/stack/sbin/profile/
	$(INSTALL) -m 0755 sles.py  $(ROOT)/export/stack/sbin/profile/
	$(INSTALL) -m 0755 utils/*.cgi $(ROOT)/export/stack/sbin/


clean::
	$(MAKE) -C utils clean

