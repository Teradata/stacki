# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack/bin
ROLLROOT 	= ../../../..
include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	# Make system directory if it doesn't exist
	mkdir -p $(ROOT)/usr/lib/systemd/system

	# Make ludicrous directory
	mkdir -p $(ROOT)/$(PKGROOT)/ludicrous

	# Install directory templates
	mkdir -p $(ROOT)/$(PKGROOT)/ludicrous/templates
	$(INSTALL) -m 0755 directory.html $(ROOT)/$(PKGROOT)/ludicrous/templates/

	# Install ludicrous server
	$(INSTALL) -m 0755 server.py $(ROOT)/$(PKGROOT)/ludicrous
	$(INSTALL) -m 0755 ludicrous-client.py $(ROOT)/$(PKGROOT)/ludicrous
	$(INSTALL) -m 0644 ludicrous-client.service $(ROOT)/usr/lib/systemd/system

	# Install ludicrous wsgi file
	$(INSTALL) -m 0644 wsgi/ludicrous-server.wsgi $(ROOT)/$(PKGROOT)/ludicrous

	# Install Apache Config file
	mkdir -p $(ROOT)/etc/apache2/stacki-conf.d
	$(INSTALL) -m0644 conf/ludicrous.conf $(ROOT)/etc/apache2/stacki-conf.d/ludicrous.conf

clean::
