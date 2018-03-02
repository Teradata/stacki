# @SI_Copyright@
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
URL		= https://releases.ansible.com/ansible
LATEST		= ansible-latest.tar.gz
DEPENDS.FILES	= $(ARCHIVENAME)-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk

getfile: 
	rm -f $(ARCHIVENAME)-*.tar.gz
	curl -s -k $(URL)/$(LATEST) -o $(LATEST)
	tar --strip-components=1 -xf $(LATEST) \
			--wildcards --no-anchored '*VERSION*'

refresh:: getfile
	(					\
		echo "NAME=foundation-ansible" > version.mk;	\
		echo "VERSION=$(shell awk '{print $$1}' VERSION)" >> version.mk; \
		echo "ARCHIVENAME=ansible" >> version.mk;	\
	)
	mv $(LATEST) $(ARCHIVENAME)-$(VERSION).tar.gz

build::
	tar -xzf $(ARCHIVENAME)-$(VERSION).tar.gz
	(					\
		cd $(ARCHIVENAME)-$(VERSION);	\
		$(PY.PATH) setup.py build;	\
	)

install::
	mkdir -p $(ROOT)
	(					\
		cd $(ARCHIVENAME)-$(VERSION);	\
		$(PY.PATH) setup.py install	\
		--root=$(ROOT);	\
	)

clean::
	rm -f VERSION
	rm -fr $(ARCHIVENAME)-$(VERSION)
