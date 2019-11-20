# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk

SRCDIRS = SLES/sles11/11sp3 SLES/sles12/12sp2 SLES/sles12/12sp3

bootstrap: # nothing to do

deploy: install-rpm
	cp /opt/stack/images/initrd*	/tftpboot/pxelinux/
	cp /opt/stack/images/vmlinuz*	/tftpboot/pxelinux/

build:
	for i in $(SRCDIRS); do \
		make -C $$i $@; \
	done

install clean nuke::
	for i in $(SRCDIRS); do \
		make -C $$i $@; \
	done
