# @copyright@
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
