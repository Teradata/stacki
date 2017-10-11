# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT   = .

-include $(ROLLSBUILD)/etc/CCRolls.mk

.PHONY: 3rdparty
3rdparty:
	$(ROLLSBUILD)/bin/get3rdparty.py

bootstrap:
	$(MAKE) -C ../common $@
	$(STACKBUILD)/bin/package-install -m "Development Tools" "Infrastructure Server"
	$(STACKBUILD)/bin/package-install createrepo genisoimage git emacs vim
	$(MAKE) 3rdparty
	$(MAKE) -C src bootstrap

preroll::
	make -C ../common rpms
	mkdir -p build-$(ROLL)-$(STACK)/RPMS
	mkdir -p build-$(ROLL)-$(STACK)/graph
	mkdir -p build-$(ROLL)-$(STACK)/nodes
	mkdir -p build-$(ROLL)-$(STACK)/manifest.d
	for d in RPMS manifest.d; do cp -r ../common/build-$(ROLL)-$(STACK)/$$d/* build-$(ROLL)-$(STACK)/$$d/; done
	for x in graph nodes; do cp -r ../common/build-$(ROLL)-$(STACK)/$$x/*.xml build-$(ROLL)-$(STACK)/$$x/; done
	cp ../common/manifest build-$(ROLL)-$(STACK)/manifest.d/common.manifest



