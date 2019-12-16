# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../..
ORDER           = 20
RPM.STRATEGY    = custom

include $(STACKBUILD)/etc/CCRules.mk

#BOOTSTRAP        =
#BOOTSTRAP.redhat =
#BOOTSTRAP.sles   =
#	$(STACKBUILD)/bin/package-install $(BOOTSTRAP) $(BOOTSTRAP.$(OS))

bootstrap rpm: src
	-for x in src/*; do $(MAKE) -C $$x $@; done
	cp manifest.d/*.manifest $(ROLLROOT)/common/manifest.d/
	cp nodes/*.xml $(ROLLROOT)/common/nodes/
	cp graph/*.xml $(ROLLROOT)/common/graph/

refresh:
	poetry update --no-interaction

src: pyproject.toml
ifeq ($(RELEASE),sles11)
	-ln -s /usr/include/apache2-worker/mpm.h /usr/include/apache2/
endif
	$(MAKE) clean
	# Add required poetry and tomlkit packages so that pip2src runs correctly.
	/opt/stack/bin/python3 -m ensurepip
	/opt/stack/bin/python3 -m pip install poetry==1.0.0
	/opt/stack/bin/python3 -m pip install tomlkit==0.5.8
# Dat dere support release is still on 3.6, and doesn't have dataclasses built in.
ifeq (Python 3.6.6,$(shell /opt/stack/bin/python3 --version))
	/opt/stack/bin/python3 -m pip install dataclasses
endif
	ROLLROOT=$(ROLLROOT) ../../stack/build/build/bin/pip2src $(RELEASE)
	mkdir -p $(ROLLROOT)/build-$(ROLL)-$(STACK)/manifest.d
	mkdir -p $(ROLLROOT)/build-$(ROLL)-$(STACK)/nodes
	mkdir -p $(ROLLROOT)/build-$(ROLL)-$(STACK)/graph

clean::
	-rm -rf src graph nodes manifest.d .cache
