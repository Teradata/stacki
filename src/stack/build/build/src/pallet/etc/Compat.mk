#
# Make rules for Compat libraries from Rolls.
#
# @SI_Copyright@
#                             www.stacki.com
#                                  v3.1
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@
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
