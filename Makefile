# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

OS=$(shell common/src/stack/build/build/bin/os)
RELEASE=$(shell common/src/stack/build/build/bin/os-release)

ROLLROOT = .

-include $(ROLLSBUILD)/etc/CCRolls.mk

ifeq ($(OS),redhat)
BOOTABLE=1
endif

.PHONY: 3rdparty
3rdparty: # we need to do the for all OSes
	cd common && $(ROLLSBUILD)/bin/get3rdparty.py
	cd redhat && $(ROLLSBUILD)/bin/get3rdparty.py
	cd sles   && $(ROLLSBUILD)/bin/get3rdparty.py

bootstrap-make:
	# setup any_python
	# this lets some of our build scripts be written in a python2 and python3
	# and scripts can use /usr/bin/env any_python for the shebang
	# note `then :;` is the bash equivalent of `pass`. skip linking if link exists
	(									\
		if [ "$(shell which any_python)" != "" ]; then :;		\
		elif [ "$(shell which python)" != "" ]; then			\
			ln -s $(shell which python) /usr/bin/any_python;	\
		elif [ "$(shell which python3)" != "" ]; then			\
			ln -s $(shell which python3) /usr/bin/any_python;	\
		fi;								\
	)
	$(MAKE) -C $(OS) -f bootstrap.mk RELEASE=$(RELEASE) bootstrap
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
	$(MAKE) -C $(OS) -f bootstrap.mk $@
	$(MAKE) -C $(OS)/src $@


preroll::
	make -C common/src pkg
	make -C $(OS)/src pkg
	mkdir -p build-$(ROLL)-$(STACK)/graph
	mkdir -p build-$(ROLL)-$(STACK)/nodes
	cp common/graph/* $(OS)/graph/* build-$(ROLL)-$(STACK)/graph/
	cp common/nodes/* $(OS)/nodes/* build-$(ROLL)-$(STACK)/nodes/

clean::
	rm -rf build-$(ROLL)-$(STACK)/graph/
	rm -rf build-$(ROLL)-$(STACK)/nodes/
