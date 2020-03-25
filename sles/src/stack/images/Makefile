# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk

# Make sure we're building the SLES os.
ifeq ($(OS), sles)
# Only build and pack up the images for the SLES release we are building.
# Add more cases to this as more SLES versions are supported, I.E.
# `else ifeq($(RELEASE), sles15)`. SLES 11 is a special case where it
# gets no bits because we package them up in SLES 12 due to being unable
# to build the image on SLES 11.
ifeq ($(RELEASE), sles12)
SRCDIRS = SLES/sles12/12sp2 SLES/sles12/12sp3 SLES/sles11/11sp3
else ifeq ($(RELEASE), sles15)
SRCDIRS = SLES/sles15/15sp1
else
SRCDIRS =
endif
endif

# Debug output of the OS, RELEASE, and SRCDIRS variables.
$(info OS is $(OS))
$(info RELEASE is $(RELEASE))
$(info SRCDIRS is $(SRCDIRS))

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
