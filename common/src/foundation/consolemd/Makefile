# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk

refresh:
	rm -fr consolemd
	git clone https://github.com/kneufeld/consolemd.git
	tar -czf consolemd.tar.gz ./consolemd

build:
	tar -xzf consolemd.tar.gz
	(							\
		cd consolemd;					\
		$(PY.PATH) setup.py build;			\
	)

install::
	mkdir -p $(ROOT)$(PKGROOT)
	(							\
		cd consolemd;					\
		$(PY.PATH) setup.py install --root $(ROOT);	\
	)

clean::
	rm -fr consolemd
