# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

ifndef __CCROLLS_MK
__CCROLLS_MK = yes

default: roll

include $(STACKBUILD)/etc/CCCommon.mk
include $(ROLLSBUILD)/etc/Rolls.mk

.PHONY: clean.all nuke.all
clean.all:: clean
	-$(MAKE) -C src clean.order
	-$(MAKE) -C src clean

nuke.all:: nuke
	-$(MAKE) -C src nuke

.PHONY: manifest-check
manifest-check:
	$(ROLLSBUILD)/bin/manifest-check.py $(ROLL) build-$(ROLL)-$(STACK)

endif # __CCROLLS_MK
