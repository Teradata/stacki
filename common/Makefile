# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

ROLLROOT = .

-include $(ROLLSBUILD)/etc/CCRolls.mk
-include version-$(ARCH).mk

.PHONY: 3rdparty
3rdparty:
	$(ROLLSBUILD)/bin/get3rdparty.py

GROUPS=developer-workstation-environment \
	compat-libraries development

PACKAGES=rpm-build redhat-rpm-config gcc \
	gcc-c++ gettext eject binutils-devel \
	byacc openssl-devel  bzip2-devel \
	ncurses-devel readline-devel \
	sqlite-devel swig gtk2-devel \
	mesa-libGLU-devel pygobject2-devel \
	pycairo-devel mkisofs libblkid-devel \
	intltool audit-libs-devel \
	system-config-keyboard cmake \
	apr-devel libcurl-devel \
	httpd-devel syslinux squashfs-tools \
	createrepo asciidoc xmlto \
	yum-utils perl-ExtUtils-MakeMaker

$(GROUPS):
	yum groupinstall -y $@

$(PACKAGES):
	yum install -y $@

ospackages: $(GROUPS) $(PACKAGES)

bootstrap: ospackages
	$(MAKE) -C src/stack/build $@
	$(MAKE) 3rdparty
	. /etc/profile.d/stack-build.sh
	$(MAKE) -C src $@

