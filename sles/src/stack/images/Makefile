# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../..

include $(STACKBUILD)/etc/CCRules.mk

# SRCDIRS = SLES/11.3 SLES/12
SRCDIRS = SLES/12

build:
	for i in $(SRCDIRS); do \
		make -C $$i $@; \
	done

install clean nuke::
	for i in $(SRCDIRS); do \
		make -C $$i $@; \
	done
