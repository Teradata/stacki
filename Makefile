# @copyright@
# @copyright@

OS=$(shell common/src/stack/build/build/bin/os)
ifeq ($(OS),redhat)
BUILDOS=centos
ROLLS.OS=redhat
else
ifeq ($(OS),suse)
BUILDOS=sles
ROLLS.OS=sles
endif
endif

ROLLROOT = .

-include $(ROLLSBUILD)/etc/CCRolls.mk

.PHONY: 3rdparty
3rdparty:
	cd common     && $(ROLLSBUILD)/bin/get3rdparty.py
	cd $(BUILDOS) && $(ROLLSBUILD)/bin/get3rdparty.py

bootstrap-make:
	$(MAKE) -C common/src/stack/build bootstrap

bootstrap: bootstrap-make
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
	$(MAKE) -C common/src $@
endif
	$(MAKE) -C $(BUILDOS) -f bootstrap.mk $@
	$(MAKE) -C $(BUILDOS)/src $@


preroll::
	cp common/manifest     build-$(ROLL)-$(STACK)/manifest.d/common.manifest
	cp $(BUILDOS)/manifest build-$(ROLL)-$(STACK)/manifest.d/$(BUILDOS).manifest
	make -C common/src     pkg
	make -C $(BUILDOS)/src pkg

