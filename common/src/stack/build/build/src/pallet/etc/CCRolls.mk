# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
	-cd $(ROLLROOT)/$(BUILDOS)/src && $(MAKE) -i clean.order clean
	-cd $(ROLLROOT)/common/src && $(MAKE) -i clean.order clean


nuke.all:: nuke
	-cd $(ROLLROOT)/$(BUILDOS)/src && $(MAKE) nuke
	-cd $(ROLLROOT)/common/src && $(MAKE) nuke
	-cd $(ROLLROOT)/ && find $(ROLLROOT) -name order-$(ROLL)*.mk -delete

.PHONY: manifest-check
manifest-check:
	$(ROLLSBUILD)/bin/manifest-check.py $(ROLL) $(REDHAT.ROOT) $(OS) $(RELEASE)

endif # __CCROLLS_MK
