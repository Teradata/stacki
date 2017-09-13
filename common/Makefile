# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

ROLLROOT = .

-include $(ROLLSBUILD)/etc/CCRolls.mk
include version.mk

.PHONY: 3rdparty
3rdparty:
	$(ROLLSBUILD)/bin/get3rdparty.py

bootstrap:: 3rdparty
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
endif
	$(MAKE) -C src bootstrap

