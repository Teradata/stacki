# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ifndef ROLL
include ../../version.mk
endif

include order-$(ROLL).mk

order-$(ROLL).mk: Makefile ../../version.mk $(shell find . -name version.mk)
	../../common/src/stack/build/build/bin/gen-order > $@

-include order-$(ROLL)-$(RELEASE).mk

clean.order:
	-rm -f order-$(ROLL).mk

bootstrap rpm pkg clean nuke:
	@for dir in $(SRCDIRS); do			\
		(cd $$dir; $(MAKE) $@);			\
	done

dump-info::
	@for x in *; do					\
		if [ -d $$x ]; then			\
			(cd $$x; $(MAKE) $@); 		\
		fi;					\
	done
