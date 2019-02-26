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
DEPENDS.FILES	= gen_random_pw.py stack-console.py yumresolver.py backup-cluster-db.sh

include $(ROCKSBUILD)/etc/CCRules.mk

ROOTONLY	= gen_random_pw yumresolver
ANYONE		= stack-console 
SCRIPTS		= $(ANYONE) $(ROOTONLY)

build:

install:: $(SCRIPTS)
	mkdir -p $(ROOT)/$(PKGROOT)/sbin/
	mkdir -p $(ROOT)/$(PKGROOT)/etc/
	mkdir -p $(ROOT)/var/db/RCS
	mkdir -p $(ROOT)/etc/cron.daily
	$(INSTALL) -m0555 $(ANYONE) $(ROOT)/$(PKGROOT)/sbin/
	$(INSTALL) -m0500 $(ROOTONLY) $(ROOT)/$(PKGROOT)/sbin/
	$(INSTALL) -m0700 backup-cluster-db.sh $(ROOT)/etc/cron.daily/backup-cluster-db

clean::
	rm -f $(SCRIPTS)

