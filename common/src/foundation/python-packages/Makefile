# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../..
ORDER           = 20
RPM.STRATEGY    = custom

include $(STACKBUILD)/etc/CCRules.mk

bootstrap rpm: src
	for x in src/*; do $(MAKE) -C $$x $@; done

refresh:
	-rm versions.json

src: packages.json
	$(MAKE) clean
	../../stack/build/build/bin/pip2src
	mkdir -p $(ROLLROOT)/build-$(ROLL)-$(STACK)/manifest.d
	mkdir -p $(ROLLROOT)/build-$(ROLL)-$(STACK)/nodes
	mkdir -p $(ROLLROOT)/build-$(ROLL)-$(STACK)/graph
	cp manifest    $(ROLLROOT)/build-$(ROLL)-$(STACK)/manifest.d/foundation-python.manifest
	cp nodes/*.xml $(ROLLROOT)/build-$(ROLL)-$(STACK)/nodes/
	cp graph/*.xml $(ROLLROOT)/build-$(ROLL)-$(STACK)/graph/

clean::
	-rm -rf src graph nodes manifest .cache


