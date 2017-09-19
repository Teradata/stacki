# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

SRCDIRS = initrd.img updates.img vmlinuz isolinux

dump-info bootstrap rpm pkg clean nuke build install:
	for x in $(SRCDIRS) ; do \
		if [ -d $$x ]; then				\
			(cd $$x; $(MAKE) $@);	 		\
		fi;				 		\
	done

