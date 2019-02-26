#
# Make rules for Compat libraries from Rolls.
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#

STACKBUILD = $(ROLLSBUILD)/../..
-include $(STACKBUILD)/etc/Rules.mk
include Rules.mk

ifndef __COMPAT_MK
__COMPAT_MK = yes

COMPATNAME=$(NAME)-compat-libs
COMPAT.RPMNAME=$(NAME)-compat-libs-$(VERSION)
RPMDB=$(CURDIR)/rpmdb/var/lib/rpm

# --------------------------------------------------------------------- #
# targets
# --------------------------------------------------------------------- #

compat-libs: compat-spec 
	mkdir -p $(RPMDB); \
	rpms=`find RPMS -name "*\.rpm"`; \
	mkdir -p rpms-here; \
	for r in $$rpms; do \
		rpm -iv --force --nodeps --badreloc --noscripts --relocate /=$(CURDIR)/rpms-here --dbpath $(RPMDB) $$r; \
	done
	$(ROLLSBUILD)/bin/make-compat-libs.py `find rpms-here -type f -perm -555` > compat-libs.txt 
	for lib in $(COMPAT.EXTRALIBS); do echo $$lib >> compat-libs.txt; done
	$(MAKE) compat-rpm

compat-rpm: rpm-mkdirs Compat.mk Rules.mk $(HOME)/.rpmmacros
	rm -f $(COMPAT.RPMNAME).tar.gz
	rm -rf $(COMPAT.RPMNAME)
	mkdir $(COMPAT.RPMNAME)
	cp compat-libs.txt Makefile arch *.mk $(COMPATNAME).spec $(COMPAT.RPMNAME)
	tar czf $(REDHAT.SOURCES)/$(COMPAT.RPMNAME).tar.gz $(COMPAT.RPMNAME)
	cp $(COMPATNAME).spec $(REDHAT.SPECS)
	rpmbuild -bb $(REDHAT.SPECS)/$(COMPATNAME).spec

compat-install:
	mkdir -p $(ROOT)/opt/x86-libs
	cpio -pdu $(ROOT)/opt/x86-libs < compat-libs.txt
	chmod -R a+rx $(ROOT)


compat-spec:
	if [ ! -f $(COMPATNAME).spec.in ] ; then \
		sed -e 's/@ROLLNAME@/$(NAME)/g' $(ROLLSBUILD)/etc/compat.spec.in > $(COMPATNAME).spec.in ; \
		$(MAKE) $(COMPATNAME).spec ; \
		rm -f $(COMPATNAME).spec.in; \
	fi 


# --------------------------------------------------------------------- #
# Copy this file into the tarball release
# --------------------------------------------------------------------- #
Compat.mk: $(wildcard $(ROLLSBUILD)/etc/Compat.mk)
	cp $^ $@


clean::
	rm -f Compat.mk
	rm -f $(COMPATNAME).spec
	rm -rf $(COMPAT.RPMNAME)
	rm -rf rpms-here
	rm -f compat-libs.txt

endif
