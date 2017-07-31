# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

dump-info bootstrap rpm pkg clean nuke build install:
	for x in initrd.img install.img vmlinuz isolinux; do	\
		if [ -d $$x ]; then				\
			(cd $$x; $(MAKE) $@);	 		\
		fi;				 		\
	done
