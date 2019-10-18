# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack/bin
ROLLROOT 	= ../../../..
include $(STACKBUILD)/etc/CCRules.mk

bootstrap: install-rpm

build:

install::
	# Install pylib
	mkdir -p $(ROOT)/$(PY.STACK)/stack/graphql
	mkdir -p $(ROOT)/$(PY.STACK)/stack/graphql/schema
	mkdir -p $(ROOT)/$(PY.STACK)/stack/graphql/templates

	(cd pylib/graphql/; find . -name "*.py" | cpio -pduv $(ROOT)/$(PY.STACK)/stack/graphql/)
	$(INSTALL) -m0644 pylib/graphql/schema/*.graphql $(ROOT)/$(PY.STACK)/stack/graphql/schema/
	$(INSTALL) -m0644 pylib/graphql/templates/*.html $(ROOT)/$(PY.STACK)/stack/graphql/templates/

	# Install WSGI File
	mkdir -p $(ROOT)/var/www/wsgi
	$(INSTALL) -m 0644 graphql-api.wsgi $(ROOT)/var/www/wsgi/stacki-graphql-api.wsgi

clean::
