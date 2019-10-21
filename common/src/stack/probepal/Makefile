# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


ROLLROOT = ../../../..
include $(STACKBUILD)/etc/CCRules.mk

bootstrap: install-rpm

build:

install::
	# Install utility
	mkdir -p $(ROOT)/opt/stack/sbin
	$(INSTALL) -m0555 bin/probepal.py $(ROOT)/opt/stack/sbin/probepal

	# Install pylib
	mkdir -p $(ROOT)/$(PY.STACK)/stack/probepal
	$(INSTALL) -m0644 pylib/*.py $(ROOT)/$(PY.STACK)/stack/probepal

clean::
