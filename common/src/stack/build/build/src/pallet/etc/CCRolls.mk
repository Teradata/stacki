# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ifndef __CCROLLS_MK
__CCROLLS_MK = yes

default: roll

include $(STACKBUILD)/etc/CCCommon.mk
include $(ROLLSBUILD)/etc/Rolls.mk

.PHONY: clean.all nuke.all
clean.all:: clean
	-$(MAKE) -C $(ROLLROOT)/src clean.order
	-$(MAKE) -C $(ROLLROOT)/src clean

nuke.all:: nuke
	-$(MAKE) -C $(ROLLROOT)/src nuke

.PHONY: manifest-check
manifest-check:
	$(ROLLSBUILD)/bin/manifest-check.py $(ROLL) build-$(ROLL)-$(STACK) $(BUILDOS)

endif # __CCROLLS_MK
