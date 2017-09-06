# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

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
