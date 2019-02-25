# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

dump-info bootstrap rpm pkg clean nuke build install:
	for x in initrd.img install.img vmlinuz isolinux; do	\
		if [ -d $$x ]; then				\
			(cd $$x; $(MAKE) $@);	 		\
		fi;				 		\
	done
