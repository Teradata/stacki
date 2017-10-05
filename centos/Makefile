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

bootstrap::
	-yum group install -y "Development Tools"
	-yum group install -y "Infrastructure Server"
	-yum install -y createrepo genisoimage git emacs vim
	$(MAKE) -C ../common $@
	$(MAKE) 3rdparty
	$(MAKE) -C src bootstrap

preroll::
	make -C ../common rpms
	mkdir -p build-$(ROLL)-$(STACK)/RPMS
	cp -r ../common/build-$(ROLL)-$(STACK)/RPMS/* build-$(ROLL)-$(STACK)/RPMS/
	cp -r ../common/manifest.d/*.manifest manifest.d/
	cp -r ../common/nodes/*.xml nodes/
	cp -r ../common/graph/*.xml graph/



