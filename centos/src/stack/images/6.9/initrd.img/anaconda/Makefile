# $Id:$
#
# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
include version.mk

PATCH_FILES = $(shell find patch-files/anaconda-$(ANACONDA_VERSION)/ -type f)

build:	loader

install:

loader: anaconda-$(ANACONDA_VERSION) $(PATCH_FILES) 
	cd patch-files && find anaconda-$(ANACONDA_VERSION) -type f | \
		grep -v CVS | cpio -pduv ../
	(								\
		cd anaconda-$(ANACONDA_VERSION) ;			\
		./configure ;						\
		make ;							\
	)
	strip -o loader anaconda-$(ANACONDA_VERSION)/loader/loader
	strip -o init anaconda-$(ANACONDA_VERSION)/loader/init


anaconda-$(ANACONDA_VERSION):
	bzcat anaconda-$(ANACONDA_VERSION).tar.bz2 | tar -x

clean::
	-rm -rf anaconda-$(ANACONDA_VERSION)
	-rm -rf patch-files/anaconda-$(ANACONDA_VERSION)/po/*mo
	-rm -f loader-network loader-pcmcia loader-local loader init

