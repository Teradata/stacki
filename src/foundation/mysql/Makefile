# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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

PKGROOT		= /opt/stack
PKGVAR		= /var/$(PKGROOT)/mysql
INSTALLDB	= $(PKGROOT)/sbin/mysql-install-db
ROLLROOT	= ../../..
DEPENDS.FILES	= mysql-$(VERSION).tar.gz
DEPENDS.DIRS	= patch-files

include $(STACKBUILD)/etc/CCRules.mk

bootstrap: install-rpm

build:
	gunzip -c mysql-$(VERSION).tar.gz | $(TAR) -xf -
	(cd patch-files && find mysql-$(VERSION) -type f | grep -v CVS | \
		cpio -pduv ../)
	( 								\
		cd mysql-$(VERSION);					\
		./configure --prefix=$(PKGROOT)				\
			--localstatedir=$(PKGVAR)			\
			--with-unix-socket-path=$(PKGVAR)/mysql.sock	\
			--with-tcp-port=40000				\
			--with-mysqld-user=stackdb			\
			--enable-thread-safe-client			\
			--with-ssl					\
			--without-debug					\
			LDFLAGS=$(MYSQL_LDFLAGS) CFLAGS=$(MYSQL_CFLAGS)	\
			;						\
		$(MAKE);						\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)/etc/
	mkdir -p $(ROOT)/$(PKGROOT)/sbin/
	mkdir -p $(ROOT)/$(PKGVAR)
	chmod a+rx $(ROOT)/$(PKGVAR)
	(								\
		cd mysql-$(VERSION);					\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT) install;		\
	)
	rm -rf $(ROOT)/$(PKGROOT)/mysql-test
	rm -rf $(ROOT)/$(PKGROOT)/sql-bench
	rm -rf $(ROOT)/var/opt/stack/mysql
	mkdir -p $(ROOT)/etc/rc.d/init.d/
	(								\
		cd mysql-$(VERSION);					\
		$(INSTALL) -m 0744 support-files/mysql.server		\
			$(ROOT)/etc/rc.d/init.d/$(NAME);		\
	)
	echo "#!/bin/bash"				>  $(ROOT)/$(INSTALLDB)
	echo "$(PKGROOT)/bin/mysql_install_db \\" 	>> $(ROOT)/$(INSTALLDB)
	echo "  --defaults-file=$(PKGROOT)/etc/my.cnf\\">> $(ROOT)/$(INSTALLDB)
	echo "	--basedir=$(PKGROOT) \\" 		>> $(ROOT)/$(INSTALLDB)
	echo "	--datadir=$(PKGVAR)  \\"		>> $(ROOT)/$(INSTALLDB)
	echo "	--user=stackdb"				>> $(ROOT)/$(INSTALLDB)
	chmod +x $(ROOT)/$(INSTALLDB)

clean::
	rm -rf mysql-$(VERSION)
