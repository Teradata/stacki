# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

rpm pkg bootstrap: src
	for x in src/*; do $(MAKE) -C $$x $@; done

refresh:
	-rm versions.json

src: packages.json pip2src
	$(MAKE) clean
	./pip2src
	cp manifest  ../../../manifest.d/foundation-python.manifest
	cp nodes/*.xml ../../../nodes/
	cp graph/*.xml ../../../graph/

clean:
	-rm -rf src graph nodes manifest

dump-info:
	@echo "NAME = foundation-python-packages"
	@echo "ORDER = 20"
	@echo "DIR = $(CURDIR)"

