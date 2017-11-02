# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk

BOOTSTRAP        = gtk3-devel gstreamer-devel
BOOTSTRAP.redhat = webkitgtk3-devel popt-devel gstreamer1-devel GConf2-devel gstreamer-python-devel gstreamer1-plugins-base-devel mesa-libGLU-devel
BOOTSTRAP.slse   = freeglut-devel gstreamer-plugins-base-devel webkit2gtk3-devel libwebkitgtk3-devel

bootstrap:
	$(STACKBUILD)/bin/package-install $(BOOTSTRAP) $(BOOTSTRAP.$(OS))

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
