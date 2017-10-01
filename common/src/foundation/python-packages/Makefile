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
		  redis pyzmq

include $(STACKBUILD)/etc/CCRules.mk

bootstrap:: install-rpm

build: 

install::
	mkdir -p $(ROOT)
	$(PY.PATH) -mpip install \
		-I --root=$(ROOT) $(PACKAGES)

#	$(PY.PATH) -mpip --disable-pip-version-check download $(PACKAGES)
#	(									\
#		$(PY.PATH) -mpip install -I --no-deps --root=$(ROOT) pytest;	\
#		for pkg in $(PACKAGES); do 					\
#			$(PY.PATH) -mpip install -I --root=$(ROOT) $$pkg;	\
#		done								\
#	)


clean::
	rm -rf *.whl
