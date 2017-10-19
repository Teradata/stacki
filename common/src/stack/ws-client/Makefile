# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


ROLLROOT = ../../../..
include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	# Install Client file
	mkdir -p $(ROOT)/opt/stack/bin
	$(INSTALL) -m0555 bin/wsclient.py $(ROOT)/opt/stack/bin/wsclient

	# Install pylib
	mkdir -p $(ROOT)/$(PY.STACK)
	$(INSTALL) -m0644 pylib/*.py $(ROOT)/$(PY.STACK)

clean::
