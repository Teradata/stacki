# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

pkg bootstrap: src
	for x in src/*; do $(MAKE) -C $$x $@; done

refresh:
	-rm versions.json

src: packages.json
	$(MAKE) clean
	./pip2src

clean:
	-rm -rf src

dump-info:
	@echo "NAME = foundation-python-packages"
	@echo "ORDER = 20"
	@echo "DIR = $(CURDIR)"

