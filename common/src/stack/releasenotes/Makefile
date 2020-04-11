# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..

COMMIT_START	= stacki-5.0.1-rhel7

include $(STACKBUILD)/etc/CCRules.mk

bootstrap: install-pkg

ReleaseNotes.txt:
	/opt/stack/bin/python3 $(PALLETBUILD)/bin/gen-release-notes.py -s $(COMMIT_START) > $@

build: ReleaseNotes.txt

install:: build
	mkdir -p $(ROOT)/$(PKGROOT)/
	install -m644 ReleaseNotes.txt $(ROOT)/$(PKGROOT)

clean::
	-rm -f ReleaseNotes.txt


