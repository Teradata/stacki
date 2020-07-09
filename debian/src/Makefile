# @copyright@
# @copyright@

ifndef ROLL
include ../../version.mk
endif

include order-$(ROLL).mk

order-$(ROLL).mk: Makefile ../../version.mk $(shell find . -name version.mk)
	python ../../common/src/stack/build/build/bin/gen-order > $@

clean.order:
	-rm -f order-$(ROLL).mk

bootstrap pkg clean nuke:
	@for dir in $(SRCDIRS); do			\
		(cd $$dir; $(MAKE) $@);			\
	done

dump-info::
	@for x in *; do					\
		if [ -d $$x ]; then			\
			(cd $$x; $(MAKE) $@); 		\
		fi;					\
	done
