# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT   = .

-include $(ROLLSBUILD)/etc/CCRolls.mk
-include bootstrap.mk

.PHONY: 3rdparty
3rdparty:
	$(ROLLSBUILD)/bin/get3rdparty.py

bootstrap::  $(GROUPS) $(PACKAGES)
	# Install package sets here
	# individual bootstrap requirement go in package
	# makefiles using the bootstrap-suse tag
	#
	# E.g. (From RedHat)
	#yum group install -y "Development Tools"
	#yum group install -y "Infrastructure Server"
	#yum install -y createrepo genisoimage emacs
	$(MAKE) -C ../common $@
	$(MAKE) 3rdparty

common:
	make -C ../common rpms

preroll:: common
	mkdir -p build-$(ROLL)-$(STACK)/RPMS
	cp -r ../common/build-$(ROLL)-$(STACK)/RPMS/* build-$(ROLL)-$(STACK)/RPMS/
