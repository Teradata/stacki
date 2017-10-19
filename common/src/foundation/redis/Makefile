# @copyright@
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES	= $(ARCHIVENAME)-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk


build:
	$(TAR) -xzf $(ARCHIVENAME)-$(VERSION).tar.gz
	(					\
		cd $(ARCHIVENAME)-$(VERSION);	\
		make PREFIX=$(PKGROOT);		\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	mkdir -p $(ROOT)/usr/lib/systemd/system
	mkdir -p $(ROOT)/etc
	mkdir -p $(ROOT)/var/spool/$(ARCHIVENAME)
	(					\
		cd $(ARCHIVENAME)-$(VERSION);	\
		make PREFIX=$(ROOT)/$(PKGROOT) install;	\
	)
	install -m644 redis.service $(ROOT)/usr/lib/systemd/system/redis.service
	install -m644 redis.conf $(ROOT)/etc/

clean::
	rm -rf $(ARCHIVENAME)-$(VERSION)
