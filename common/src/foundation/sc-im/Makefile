# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

PKGROOT		= /opt/stack/$(ARCHIVENAME)
ROLLROOT	= ../../../..
DEPENDS.FILES	= $(ARCHIVENAME)-$(VERSION)-$(RELEASE).tgz

include $(STACKBUILD)/etc/CCRules.mk

bootstrap:
ifeq ($(OS),sles)
	echo "Name: ncursesw" > /usr/lib64/pkgconfig/ncursesw.pc
	echo "Description: Old school GUI" >> /usr/lib64/pkgconfig/ncursesw.pc
	echo "Version: 5.9-40"  >> /usr/lib64/pkgconfig/ncursesw.pc
	echo "Libs: -lncursesw" >> /usr/lib64/pkgconfig/ncursesw.pc
endif


refresh:
	git clone https://github.com/andmarti1424/sc-im.git
	(cd $(ARCHIVENAME) ; git archive --format=tgz HEAD > \
		../$(ARCHIVENAME)-$(VERSION)-`date +%Y%m%d`.tgz)

build:
	mkdir $(ARCHIVENAME)
	(cd $(ARCHIVENAME) ; tar zvfx ../$(ARCHIVENAME)-$(VERSION)-$(RELEASE).tgz)
	(cd $(ARCHIVENAME)/src ; $(MAKE) prefix=$(PKGROOT))

install::
	echo
	echo
	env
	echo
	echo
	(cd $(ARCHIVENAME)/src ; $(MAKE) prefix=$(ROOT)/$(PKGROOT) install)

clean::
	rm -rf $(ARCHIVENAME)

