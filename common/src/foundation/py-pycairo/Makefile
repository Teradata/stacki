# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= pycairo-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk


build:
	gunzip -c pycairo-$(VERSION).tar.gz | $(TAR) -xf -
	(							\
		cd pycairo-$(VERSION);				\
		$(PY.PATH) setup.py build;			\
	)

install::
	(							\
		cd pycairo-$(VERSION);				\
		$(PY.PATH) setup.py install --root=$(ROOT);	\
	)


clean::
	rm -rf pycairo-$(VERSION)

