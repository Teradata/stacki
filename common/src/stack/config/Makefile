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

ROLLROOT	= ../../..
DEPENDS.DIRS	= etc init.d
STACKBUILD      = $(ROLLROOT)/src/stack/build/build

include $(STACKBUILD)/etc/CCRules.mk

bootstrap:: install-rpm

build:

install::
	mkdir -p $(ROOT)/etc/profile.d/
	$(INSTALL) -m755 etc/profile.d/*sh	$(ROOT)/etc/profile.d/
	mkdir -p $(ROOT)/etc/rc.d/init.d
	$(INSTALL) -m755 init.d/stack-dmesg	$(ROOT)/etc/rc.d/init.d/
	$(INSTALL) -m755 init.d/stack-pre	$(ROOT)/etc/rc.d/init.d/
	$(INSTALL) -m755 init.d/stack-post	$(ROOT)/etc/rc.d/init.d/

