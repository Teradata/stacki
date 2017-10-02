# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
PACKAGES	= pytest pymysql PyYAML Jinja2 \
		  six Flask requests flake8 \
		  ConfigParser python-daemon lockfile \
		  redis pyzmq testinfra

include $(STACKBUILD)/etc/CCRules.mk

bootstrap:: install-rpm

build: 

install::
	mkdir -p $(ROOT)
	$(PY.PATH) -mpip install \
		-I --root=$(ROOT) $(PACKAGES)


clean::
	rm -rf *.whl
