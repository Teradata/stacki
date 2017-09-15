# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#

PKGROOT		= /opt/stack/$(NAME)
ROLLROOT	= ../../..
DEPENDS.FILES	= $(NAME)-$(VERSION)-$(RELEASE).tgz

include $(STACKBUILD)/etc/CCRules.mk
-include build-$(OS).mk


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

