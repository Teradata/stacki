# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= $(wildcard *.py) setDbPartitions.cgi


include $(STACKBUILD)/etc/CCRules.mk


build::

install::
	mkdir -p $(ROOT)/export/stack/sbin/profile
	$(INSTALL) -m 0755 profile.py  $(ROOT)/export/stack/sbin/profile.cgi
	$(INSTALL) -m 0755 __init__.py $(ROOT)/export/stack/sbin/profile/
	$(INSTALL) -m 0755 redhat.py  $(ROOT)/export/stack/sbin/profile/
	$(INSTALL) -m 0755 sles.py  $(ROOT)/export/stack/sbin/profile/
	$(INSTALL) -m 0755 setDbPartitions.cgi $(ROOT)/export/stack/sbin/
