#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

ROLLROOT = ../../../..
include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	# Install WSGI File
	mkdir -p $(ROOT)/var/www/wsgi
	$(INSTALL) -m0644 cgi-bin/wsgi.py $(ROOT)/var/www/wsgi/stacki-ws.wsgi

	# Install Django Setup files
	mkdir -p $(ROOT)/opt/stack/share/stack/bin
	$(INSTALL) -m0700 setup/* $(ROOT)/opt/stack/share/stack/bin/

	# Install REST API Files
	mkdir -p $(ROOT)/$(PY.STACK)/stack
	find restapi -type f -name \*.py | cpio -pudv $(ROOT)/$(PY.STACK)/stack/

	# Install Command line and pylib
	mkdir -p $(ROOT)/$(PY.STACK)/stack/commands
	$(INSTALL) -m0644 pylib/*.py $(ROOT)/$(PY.STACK)/stack/
	(					\
		cd command;			\
		find . -type f -name \*.py |	\
		cpio -pudv $(ROOT)/$(PY.STACK)/stack/commands;	\
	)
	find $(ROOT)/$(PY.STACK)/stack/commands -name "*.py" | $(AWK)	\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'  

	# Install syslog file
	mkdir -p $(ROOT)/etc/rsyslog.d/
	$(INSTALL) -m0644 conf/stacki_ws.syslog $(ROOT)/etc/rsyslog.d/stacki_ws.conf

clean::
