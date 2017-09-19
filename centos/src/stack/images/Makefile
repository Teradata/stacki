# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../..

include $(STACKBUILD)/etc/CCRules.mk
-include $(RELEASE).mk
-include $(RELEASE)-$(ARCH).mk


#bootstrap:
#	yum install -y $(OS.DEPENDENCIES)

deploy: install-rpm
	cp /opt/stack/images/initrd*	/tftpboot/pxelinux/
	cp /opt/stack/images/vmlinuz*	/tftpboot/pxelinux/

build:
	make -C $(ANACONDA_VERSION) build

install::
	make -C $(ANACONDA_VERSION) install

clean::
	make -C $(ANACONDA_VERSION) clean

nuke::
	make -C $(ANACONDA_VERSION) nuke

