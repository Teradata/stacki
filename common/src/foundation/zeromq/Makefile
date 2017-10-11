# @copyright@
# @copyright@
#

ROLLROOT = ../../..
PKGROOT=/opt/stack
DEPENDS.FILES=$(ARCHIVENAME)-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk


bootstrap: install-rpm

build:
	tar xzf $(ARCHIVENAME)-$(VERSION).tar.gz
	(\
		cd $(ARCHIVENAME)-$(VERSION);	\
		PKG_CONFIG_PATH=$(PKGROOT)/lib/pkgconfig/ \
		./configure --prefix=$(PKGROOT);\
		$(MAKE);			\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(\
		cd $(ARCHIVENAME)-$(VERSION);	\
		$(MAKE) DESTDIR=$(ROOT) install;\
	)

clean::
	rm -rf $(ARCHIVENAME)-$(VERSION)
