# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk

refresh:
	rm -fr fbtftp
	git clone https://github.com/facebook/fbtftp.git
	tar -czf fbtftp.tar.gz ./fbtftp
	
build:
	(					\
		tar -xzf fbtftp.tar.gz;		\
		cd fbtftp;			\
		$(PY.PATH) setup.py build;	\
	)

install::
	(					\
		mkdir -p $(ROOT)$(PKGROOT)/bin;	\
		mkdir -p $(ROOT)/usr/lib/systemd/system; \
		cd fbtftp;			\
		$(PY.PATH) setup.py install 	\
		--root $(ROOT);			\
		$(INSTALL) -m 755 ./examples/server.py \
			$(ROOT)$(PKGROOT)/bin/in.fbtftpd; \
		$(INSTALL) ../systemd/fbtftpd.service \
			$(ROOT)/usr/lib/systemd/system/; \
	)

clean::
	rm -fr fbtftp
