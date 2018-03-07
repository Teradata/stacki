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

	# Install directory templates
	mkdir -p $(ROOT)/$(PKGROOT)/templates
	$(INSTALL) -m 0755 directory.html $(ROOT)/$(PKGROOT)/templates/

	# Install ludicrous server
	$(INSTALL) -m 0755 ludicrousServer.py $(ROOT)/$(PKGROOT)
	$(INSTALL) -m 0755 ludicrous-client.py $(ROOT)/$(PKGROOT)
	$(INSTALL) -m 0644 ludicrous-client.service $(ROOT)/usr/lib/systemd/system


	# Install WSGI File
	mkdir -p $(ROOT)/var/www/cgi-bin
	$(INSTALL) -m 0644 wsgi/ludicrous-server.wsgi $(ROOT)/var/www/cgi-bin/ludicrous.py

	# Install Apache Config file done in xml now

clean::
