# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk

SRCDIRS = SLES/11.3/1.138 SLES/12/sp2 SLES/12/sp3

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
