# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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
SCRIPTS		= insert-ethers
PLUGINS		= $(wildcard plugins/*py)
PLUGINDIR	= $(PKGROOT)/var/plugins/insertethers
ROLLROOT	= ../../../..
DEPENDS.FILES	= backup-cluster-db.sh insert-ethers.py insert-ethersrc.xml 
DEPENDS.DIRS	= plugins po

include $(STACKBUILD)/etc/CCRules.mk

RCFILES = staterc insert-ethersrc

po ::
	$(MAKE) -C po

build: $(SCRIPTS) $(RCFILES) po

install:: build
	mkdir -p $(ROOT)/$(PKGROOT)/sbin/
	mkdir -p $(ROOT)/$(PKGROOT)/etc/
	mkdir -p $(ROOT)/var/db/RCS
	mkdir -p $(ROOT)/$(PLUGINDIR)
	mkdir -p $(ROOT)/etc/cron.daily
	$(INSTALL) -m 0544 $(SCRIPTS) $(ROOT)/$(PKGROOT)/sbin/
	$(INSTALL) -m 0644  $(RCFILES) $(ROOT)/$(PKGROOT)/etc/
	$(INSTALL) -m 0700 backup-cluster-db.sh \
		$(ROOT)/etc/cron.daily/backup-cluster-db
	$(INSTALL) -m 0644 $(PLUGINS) $(ROOT)/$(PLUGINDIR)

	$(MAKE) install -C po 


clean::
	rm -f $(SCRIPTS)

