# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

ifndef ROLL
include ../../version.mk
endif

RELEASE = $(shell $(STACKBUILD)/bin/redhat-release)
bootstrap rpm pkg clean nuke dump-info:
	make -C $(RELEASE) $@
