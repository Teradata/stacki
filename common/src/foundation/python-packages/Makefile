# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..

include $(STACKBUILD)/etc/CCRules.mk

refresh:
	-rm versions.json

build:
	$(MAKE) clean
	./pip2src

bootstrap::
	for d in src/*; do $(MAKE) -C $$d $@; done

pkg: build
	for d in src/*; do $(MAKE) -C $$d $@; done


clean::
	-rm -rf src
