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

PKGROOT		= /
ROLLROOT	= ../../../..
DEPENDS.DIRS	= init.d profile.d cgi mq

include $(ROCKSBUILD)/etc/CCRules.mk

build::

install::
	mkdir -p $(ROOT)/etc/profile.d/
	mkdir -p $(ROOT)/etc/init.d/
	mkdir -p $(ROOT)/export/stack/pallets
	mkdir -p $(ROOT)/$(PY.STACK)/stack/mq/producers
	$(INSTALL) -m755 profile.d/ssh-key.sh $(ROOT)/etc/profile.d/
	$(INSTALL) -m755 init.d/stack-num-cpus $(ROOT)/etc/init.d/
	$(INSTALL) -m755 cgi/index.cgi $(ROOT)/export/stack/pallets/index.cgi
	$(INSTALL) -m755 cgi/pallets.cgi $(ROOT)/export/stack/pallets/pallets.cgi
	$(INSTALL) -m644 mq/producers/switch_health.py $(ROOT)/$(PY.STACK)/stack/mq/producers/

