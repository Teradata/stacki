# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT = .

-include $(ROLLSBUILD)/etc/CCRolls.mk
include version.mk

.PHONY: 3rdparty
3rdparty:
	$(ROLLSBUILD)/bin/get3rdparty.py

bootstrap::
	$(MAKE) -C src/stack/build $@
	$(MAKE) -C src/stack/config $@
ifeq ($(STACKBUILD),)
	@echo
	@echo
	@echo Stacki build environment is now installed. Before you can
	@echo continue you will need to logout and login again. Then re-run
	@echo "make bootstrap" again.
	@echo
	@echo
	@/bin/false # stop the caller from continuing
else
	$(MAKE) 3rdparty
	$(MAKE) -C src bootstrap
endif
