#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

ifndef ROLL
include ../version.mk
endif

include order-$(ROLL).mk

order-$(ROLL).mk: Makefile ../version.mk $(shell find . -name version.mk)
	$(STACKBUILD)/bin/gen-order > $@


clean.order:
	-rm -f order-$(ROLL).mk

bootstrap rpm pkg clean nuke:
	@for dir in $(SRCDIRS); do			\
		(cd $$dir; $(MAKE) $@);			\
	done

dump-info::
	@for x in $(SRCDIRS); do			\
		if [ -d $$x ]; then			\
			(cd $$x; $(MAKE) $@); 		\
		fi;					\
	done
