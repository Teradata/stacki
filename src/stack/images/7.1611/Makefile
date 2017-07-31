# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

SRCDIRS = initrd.img updates.img vmlinuz isolinux

dump-info bootstrap rpm pkg clean nuke build install:
	for x in $(SRCDIRS) ; do \
		if [ -d $$x ]; then				\
			(cd $$x; $(MAKE) $@);	 		\
		fi;				 		\
	done

