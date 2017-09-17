# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

PKGROOT		= /opt/stack
PKGVAR		= /var/$(PKGROOT)/mysql
INSTALLDB	= $(PKGROOT)/sbin/mysql-install-db
ROLLROOT	= ../../..
DEPENDS.FILES	= mariadb-$(VERSION).tar.gz
#DEPENDS.DIRS	= patch-files

include $(STACKBUILD)/etc/CCRules.mk

bootstrap-redhat::
	yum install -y cmake systemd-devel

build:
	gunzip -c mariadb-$(VERSION).tar.gz | $(TAR) -xf -
	-(cd patch-files && find mariadb-$(VERSION) -type f | cpio -pudv ../ )
	( 						\
		cd mariadb-$(VERSION);			\
		cmake -DCMAKE_INSTALL_PREFIX=$(PKGROOT)	\
			-DGROONGA_NORMALIZER_MYSQL_EMBED=OFF \
			-DMRN_GROONGA_EMBED=OFF \
			-DMRN_GROONGA_NORMALIZER_MYSQL_EMBED=OFF \
			-DPLUGIN_ARCHIVE=NO \
			-DPLUGIN_CONNECT=NO \
			-DPLUGIN_FEDERATED=NO \
			-DPLUGIN_FEDERATEDX=NO \
			-DPLUGIN_MROONGA=NO \
			-DPLUGIN_ROCKSDB=NO \
			-DPLUGIN_SEQUENCE=NO \
			-DPLUGIN_SPHINX=NO \
			-DPLUGIN_SPIDER=NO \
			-DPLUGIN_TOKUDB=NO \
			-DWITH_UNIT_TESTS=OFF \
			-DHAVE_SYSTEMD=YES \
			-DMYSQLD_USER=stackdb \
			-DINSTALL_LAYOUT=RPM		\
			-DINSTALL_MYSQLDATADIR=$(PKGVAR)\
			-DINSTALL_SYSCONFDIR=$(PKGROOT)/etc \
			-DINSTALL_SYSCONF2DIR=$(PKGROOT)/etc/my.cnf.d \
			-DMYSQL_TCP_PORT=40000;		\
		$(MAKE);				\
	)


install::
	mkdir -p $(ROOT)/$(PKGROOT)/etc/
	mkdir -p $(ROOT)/$(PKGROOT)/sbin/
	mkdir -p $(ROOT)/usr/lib/systemd/system/
	(						\
		cd mariadb-$(VERSION);			\
		$(MAKE) DESTDIR=$(ROOT) install;	\
	)
	rm -rf $(ROOT)/$(PKGROOT)/share/mysql-test
	echo "#!/bin/bash"				>  $(ROOT)/$(INSTALLDB)
	echo "$(PKGROOT)/bin/mysql_install_db \\" 	>> $(ROOT)/$(INSTALLDB)
	echo "  --defaults-file=$(PKGROOT)/etc/my.cnf\\">> $(ROOT)/$(INSTALLDB)
	echo "	--basedir=$(PKGROOT) \\" 		>> $(ROOT)/$(INSTALLDB)
	echo "	--datadir=$(PKGVAR)  \\"		>> $(ROOT)/$(INSTALLDB)
	echo "	--user=stackdb"				>> $(ROOT)/$(INSTALLDB)
	chmod +x $(ROOT)/$(INSTALLDB)

clean::
	rm -rf mariadb-$(VERSION)
