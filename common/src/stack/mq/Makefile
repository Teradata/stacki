# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.DIRS	= daemons producers processors clients

include $(STACKBUILD)/etc/CCRules.mk

bootstrap: install-pkg

build:

install::
	mkdir -p $(ROOT)/$(PY.STACK)/stack/mq/producers
	mkdir -p $(ROOT)/$(PY.STACK)/stack/mq/processors
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	mkdir -p $(ROOT)/etc/init.d
	mkdir -p $(ROOT)/etc/systemd/system
	# client
	$(INSTALL) -m 0755 clients/publish.py		$(ROOT)/$(PKGROOT)/bin/smq-publish
	$(INSTALL) -m 0755 clients/channel-ctrl.py	$(ROOT)/$(PKGROOT)/bin/channel-ctrl
	# daemons
	$(INSTALL) -m 0755 daemons/producer.py		$(ROOT)/$(PKGROOT)/sbin/smq-producer
	$(INSTALL) -m 0755 daemons/publisher.py		$(ROOT)/$(PKGROOT)/sbin/smq-publisher
	$(INSTALL) -m 0755 daemons/shipper.py		$(ROOT)/$(PKGROOT)/sbin/smq-shipper
	$(INSTALL) -m 0755 daemons/processor.py		$(ROOT)/$(PKGROOT)/sbin/smq-processor
	# init files
	$(INSTALL) -m 0755 daemons/init.d/*		$(ROOT)/etc/init.d/
	$(INSTALL) -m 0644 daemons/systemd/*		$(ROOT)/etc/systemd/system/
	# producers / processors / pylib
	$(INSTALL) -m 0644 $(wildcard producers/*.py)	$(ROOT)/$(PY.STACK)/stack/mq/producers/
	$(INSTALL) -m 0644 $(wildcard processors/*.py)	$(ROOT)/$(PY.STACK)/stack/mq/processors/
	$(INSTALL) -m 0644 $(wildcard pylib/mq/*.py)	$(ROOT)/$(PY.STACK)/stack/mq/



