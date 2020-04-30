# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..
DEPENDS.FILES   = fbtftp-$(VERSION).tar.gz

include $(STACKBUILD)/etc/CCRules.mk

refresh:
	rm -fr fbtftp
	git clone https://github.com/facebook/fbtftp.git
	tar -czf fbtftp-$(shell date --rfc-3339=date).tar.gz ./fbtftp
	
build:
	(					\
		tar -xzf fbtftp-$(VERSION).tar.gz;		\
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
