# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
PACKAGES	= pytest pymysql PyYAML Jinja2 six Flask requests flake8

include $(STACKBUILD)/etc/CCRules.mk

bootstrap:: install-rpm

build: 
	$(PY.PATH) -mpip download $(PACKAGES)


install::
	mkdir -p $(ROOT)
	(									\
		for pkg in $(PACKAGES); do 					\
			$(PY.PATH) -mpip install -I --root=$(ROOT) $$pkg;	\
		done								\
	)


clean::
	rm -rf *.whl
