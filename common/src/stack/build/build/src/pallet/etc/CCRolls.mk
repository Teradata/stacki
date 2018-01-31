# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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
	-$(MAKE) -C $(ROLLROOT)/$(BUILDOS)/src clean.order
	-$(MAKE) -C $(ROLLROOT)/$(BUILDOS)/src clean
	-$(MAKE) -C $(ROLLROOT)/common/src clean.order
	-$(MAKE) -C $(ROLLROOT)/common/src clean

nuke.all:: nuke
	-$(MAKE) -C $(ROLLROOT)/$(BUILDOS)/src nuke
	-$(MAKE) -C $(ROLLROOT)/common/src nuke

.PHONY: manifest-check
manifest-check:
	$(ROLLSBUILD)/bin/manifest-check.py $(ROLL) build-$(ROLL)-$(STACK) $(OS) $(RELEASE)

endif # __CCROLLS_MK
