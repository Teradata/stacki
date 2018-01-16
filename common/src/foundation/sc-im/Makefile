# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

PKGROOT		= /opt/stack/$(NAME)
ROLLROOT	= ../../../..
DEPENDS.FILES	= $(NAME)-$(VERSION)-$(RELEASE).tgz

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
	(cd $(NAME) ; git archive --format=tgz HEAD > \
		../$(NAME)-$(VERSION)-`date +%Y%m%d`.tgz)

build:
	mkdir $(NAME)
	(cd $(NAME) ; tar zvfx ../$(NAME)-$(VERSION)-$(RELEASE).tgz)
	(cd $(NAME)/src ; $(MAKE) prefix=$(PKGROOT))

install::
	echo
	echo
	env
	echo
	echo
	(cd $(NAME)/src ; $(MAKE) prefix=$(ROOT)/$(PKGROOT) install)

clean::
	rm -rf $(NAME)

