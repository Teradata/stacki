# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT         = /opt/@template@
TARBALL_POSTFIX = tgz
ROLLROOT	= ../..

include $(STACKBUILD)/etc/CCRules.mk

build:
	gunzip -c $(NAME)-$(VERSION).$(TARBALL_POSTFIX) | $(TAR) -xf -
	( 							\
		cd $(NAME)-$(VERSION);				\
		./configure --prefix=$(PKGROOT)/$(NAME);	\
		$(MAKE);					\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)/$(NAME)
	(							\
		cd $(NAME)-$(VERSION);				\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT)/$(NAME) install;\
	)

clean::
	rm -rf $(NAME)-$(VERSION)
