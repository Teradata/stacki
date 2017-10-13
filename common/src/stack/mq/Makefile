# @copyright@
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.DIRS	= daemons producers processors clients

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PY.STACK)/stack/mq/producers
	mkdir -p $(ROOT)/$(PY.STACK)/stack/mq/processors
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	mkdir -p $(ROOT)/etc/init.d/
	# client
	$(INSTALL) -m 0755 clients/publish.py		$(ROOT)/$(PKGROOT)/bin/rmq-publish
	$(INSTALL) -m 0755 clients/channel-ctrl.py	$(ROOT)/$(PKGROOT)/bin/channel-ctrl
	# daemons
	$(INSTALL) -m 0755 daemons/producer.py		$(ROOT)/$(PKGROOT)/sbin/rmq-producer
	$(INSTALL) -m 0755 daemons/publisher.py		$(ROOT)/$(PKGROOT)/sbin/rmq-publisher
	$(INSTALL) -m 0755 daemons/shipper.py		$(ROOT)/$(PKGROOT)/sbin/rmq-shipper
	$(INSTALL) -m 0755 daemons/processor.py		$(ROOT)/$(PKGROOT)/sbin/rmq-processor
	# init files
	$(INSTALL) -m 0755 daemons/producer.init	$(ROOT)/etc/init.d/rmq-producer
	$(INSTALL) -m 0755 daemons/publisher.init	$(ROOT)/etc/init.d/rmq-publisher
	$(INSTALL) -m 0755 daemons/shipper.init		$(ROOT)/etc/init.d/rmq-shipper
	$(INSTALL) -m 0755 daemons/processor.init	$(ROOT)/etc/init.d/rmq-processor
	# producers / processors / pylib
	$(INSTALL) -m 0644 $(wildcard producers/*.py)	$(ROOT)/$(PY.STACK)/stack/mq/producers/
	$(INSTALL) -m 0644 $(wildcard processors/*.py)	$(ROOT)/$(PY.STACK)/stack/mq/processors/
	$(INSTALL) -m 0644 $(wildcard pylib/mq/*.py)	$(ROOT)/$(PY.STACK)/stack/mq/



