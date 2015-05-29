ROLLROOT	= ../../..
DEPENDS.FILES	= $(PYREQUESTS_NAME)-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk

bootstrap: install-rpm

build:
	tar -xf $(PYREQUESTS_NAME)-$(VERSION).tar.gz
	(					\
		cd $(PYREQUESTS_NAME)-$(VERSION);	\
		$(PY.PATH) setup.py build;	\
	)

install::
	(					\
		cd $(PYREQUESTS_NAME)-$(VERSION);	\
		$(PY.PATH) setup.py install --root=$(ROOT); \
	)


clean::
	rm -rf $(PYREQUESTS_NAME)-$(VERSION)
