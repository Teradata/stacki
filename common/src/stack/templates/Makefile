# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

ROLLROOT	= ../../../..
DEPENDS.FILES	= $(wildcard *j2)
include $(STACKBUILD)/etc/CCRules.mk

ifeq ($(ROLLVERSION),)
ROLLVERSION = $(RPM_PACKAGE_VERSION)
endif


build:
	echo "Building templates"

install::
	mkdir -p $(ROOT)/opt/stack/share/templates/
	@for fil in *.j2; do	\
		$(INSTALL) -m444 $$fil $(ROOT)/opt/stack/share/templates/$$fil ; \
	done

