# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ifndef ROLL
include ../../version.mk
endif

RELEASE = $(shell $(STACKBUILD)/bin/os-release)

bootstrap rpm pkg clean nuke dump-info:
	make -C $(RELEASE) $@
