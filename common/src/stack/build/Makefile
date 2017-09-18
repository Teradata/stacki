# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

PKGROOT		= /opt/stack/share/build
STACKBUILD	= build
ROLLROOT	= ../../..
DEPENDS.DIRS	= build
DEPENDS.FILES	= stack-build.sh stack-build.csh
DEPENDS.RPMS	=

include $(STACKBUILD)/etc/CCRules.mk

bootstrap:: install-rpm

build:

install::
	mkdir -p $(ROOT)/$(PKGROOT)/
	mkdir -p $(ROOT)/etc/profile.d/
	mkdir -p $(ROOT)/opt/stack/share/licenses/
	$(INSTALL) -m0555 stack-build.sh  $(ROOT)/etc/profile.d
	$(INSTALL) -m0555 stack-build.csh $(ROOT)/etc/profile.d
	(								\
		cd LICENSE;						\
		find . -type f | cpio -pudv $(ROOT)/opt/stack/share/licenses/; \
	)
	(								\
		cd build;						\
		find . | cpio -pduv $(ROOT)/$(PKGROOT)/;		\
	)

