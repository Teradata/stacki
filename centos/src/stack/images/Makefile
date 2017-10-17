# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk
-include $(RELEASE).mk
-include $(RELEASE)-$(ARCH).mk

BOOTSTRAP = NetworkManager-devel	\
	NetworkManager-glib-devel	\
	libnl-devel			\
	device-mapper-devel		\
	rpm-devel			\
	libarchive-devel		\
	isomd5sum-devel			\
	e2fsprogs-devel			\
	iscsi-initiator-utils-devel	\
	newt-devel			\
	squashfs-tools

bootstrap:
	$(STACKBUILD)/bin/package-install $(BOOTSTRAP)


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

