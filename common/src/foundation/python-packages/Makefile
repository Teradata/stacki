# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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
	-rm -f versions.json

src: packages.json
ifeq ($(RELEASE),sles11)
	-ln -s /usr/include/apache2-worker/mpm.h /usr/include/apache2/
endif
	$(MAKE) clean
	ROLLROOT=$(ROLLROOT) ../../stack/build/build/bin/pip2src
	mkdir -p $(ROLLROOT)/build-$(ROLL)-$(STACK)/manifest.d
	mkdir -p $(ROLLROOT)/build-$(ROLL)-$(STACK)/nodes
	mkdir -p $(ROLLROOT)/build-$(ROLL)-$(STACK)/graph

clean::
	-rm -rf src graph nodes manifest.d .cache


