# @copyright@
# @copyright@

PKGROOT     = /opt/stack
ROLLROOT    = ../../../..
DEPENDS.DIR = pylib init.d systemd 

include $(STACKBUILD)/etc/CCRules.mk

bootstrap: install-rpm

build:

install::
	# Copy BackendTest.py to /opt/stack/bin
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	$(INSTALL) -m 755 BackendTest.py $(ROOT)/$(PKGROOT)/bin

	# Copy checklist file to /opt/stack/bin
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	$(INSTALL) -m 0755 checklist.py $(ROOT)/$(PKGROOT)/bin

	# Copy threads as pylib files
	mkdir -p $(ROOT)/$(PY.STACK)/stack/checklist/
	 $(INSTALL) -m 755 pylib/*.py $(ROOT)/$(PY.STACK)/stack/checklist/

	mkdir -p $(ROOT)/$(PY.STACK)/stack/checklist/threads
	$(INSTALL) -m 755 pylib/threads/*.py $(ROOT)/$(PY.STACK)/stack/checklist/threads/

	# Copy service filei
	mkdir -p $(ROOT)/usr/lib/systemd/system
	$(INSTALL) -m 0644 systemd/checklist.service $(ROOT)/usr/lib/systemd/system

	mkdir -p $(ROOT)/etc/init.d/
	$(INSTALL) -m 0644 init.d/checklist $(ROOT)/etc/init.d
