# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..

include $(STACKBUILD)/etc/CCRules.mk

bootstrap-redhat::
	yum install -y webkitgtk3-devel gtk3-devel gstreamer-devel popt-devel gstreamer1-devel GConf2-devel gstreamer-python-devel gstreamer1-plugins-base-devel mesa-libGLU-devel

build:
	tar -xzf wxPython-$(VERSION).tar.gz
	(								\
		cd wxPython-$(VERSION);					\
		$(PY.PATH) ./build.py build 				\
			--gtk3						\
			--destdir=$(PKGROOT);				\
	)

install::
	(								\
		cd wxPython-$(VERSION);					\
		$(PY.PATH) ./build.py install				\
			--gtk3						\
			--destdir=$(ROOT) 				\
			--prefix=$(PKGROOT);				\
	)

clean::
	rm -rf wxPython-$(VERSION)
