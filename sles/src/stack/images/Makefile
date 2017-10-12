# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../..

include $(STACKBUILD)/etc/CCRules.mk

SRCDIRS = SLES/11.3 SLES/12

bootstrap: # nothing to do

build:
	for i in $(SRCDIRS); do \
		make -C $$i $@; \
	done

install clean nuke::
	for i in $(SRCDIRS); do \
		make -C $$i $@; \
	done
