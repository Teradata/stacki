# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= $(NAME).tar.gz
DEPENDS.DIRS	= extras
include $(STACKBUILD)/etc/CCRules.mk

build:
	$(TAR) xf $(NAME).tar.gz
	(			\
		cd $(NAME);	\
		$(MAKE) $(BINARY); \
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	mkdir -p $(ROOT)/$(PY.STACK)/salt/modules
	$(INSTALL) -m0755 $(NAME)/$(BINARY) $(ROOT)/$(PKGROOT)/bin
	$(INSTALL) -m0644 extras/stream.py $(ROOT)/$(PY.STACK)/salt/modules/stream.py

clean::
	rm -rf $(NAME)

