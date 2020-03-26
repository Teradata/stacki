# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

ifndef __RULES_REDHAT_MK
__RULES_REDHAT_MK = yes

# --------------------------------------------------------------------- #
# OS Dependent Stuff
# --------------------------------------------------------------------- #
PYTHON  = /opt/stack/bin/python
WEBSERVER_ROOT = /var/www/html
PATCH   = patch
USERID = $(shell id -u)
INSTALL = install
CVS	= /usr/bin/cvs
#MYSQL_LDFLAGS = -all-static
TARGET_PKG = rpm
TAR = tar
INIT_SCRIPTS_DIR = /etc/rc.d/init.d
PROFILE_DIR = /export/profile
MPIROOT	= /opt/openmpi

ifneq ($(shell echo *.spec.in),*.spec.in)
RPM.OLDSTYLE = 1
endif

RPM.STRATEGY ?= source
RPM.FILESLIST = /tmp/$(NAME)-fileslist

# --------------------------------------------------------------------- #
# Roll kickstart profiles building need a few special settings
# --------------------------------------------------------------------- #
ifdef __ROLLS_MK
RPM.PACKAGE = kickstart
RPM.ARCH = noarch
RPM.SUMMARY = StackIQ $(ROLL) Roll
RPM.DESCRIPTION = XML files for the StackIQ $(ROLL) Roll
RPM.PREFIX = $(PROFILE_DIR)
endif

ifndef ROLL.MEMBERSHIP
ROLL.MEMBERSHIP = $(ROLL)
endif


# --------------------------------------------------------------------- #
# RPM.STRATEGY = copy
# copy binary rpms into top level RPMS/<arch> directories
# --------------------------------------------------------------------- #
ifeq ($(RPM.STRATEGY),copy)


ifeq ($(filter $(ROLL), $(ROLL.MEMBERSHIP)),$(ROLL))


include $(STACKBUILD)/etc/copy.mk


else
rpm:
	@echo $(NAME) is not a member of $(ROLL)
endif

endif

# --------------------------------------------------------------------- #
# Copy into /usr/src/redhat (must be done as root)
# Build Package 
# --------------------------------------------------------------------- #

BUILD.PREFIX ?= build
REDHAT.ROOT  ?= $(CURDIR)/$(ROLLROOT)/$(BUILD.PREFIX)-$(ROLL)-$(STACK)
REDHAT.VAR   ?= /var

REDHAT.SOURCES	= $(REDHAT.ROOT)/SOURCES
REDHAT.SPECS	= $(REDHAT.ROOT)/SPECS
REDHAT.BUILD	= $(REDHAT.ROOT)/BUILD
REDHAT.RPMS	= $(REDHAT.ROOT)/RPMS
REDHAT.SRPMS	= $(REDHAT.ROOT)/SRPMS

ifeq ($(RPMNAME),)
RPMNAME		:= $(NAME)-$(VERSION)
else
RPMNAME		:= $(RPMNAME)-$(VERSION)
endif


TARBALL		= $(RPMNAME).tar
TARBALL.GZ	= $(TARBALL).gz
SPECFILE	= $(NAME).spec

HOME		= $(CURDIR)

# @echo "%__arch_install_post	%{nil}" >> $@

$(REDHAT.SOURCES)/$(TARBALL): clean
	$(MAKE) pretar 
	#@if [ `basename $(CURDIR)` = usersguide ]; then $(MAKE) predoc; fi;
	@rm -rf $(RPMNAME)
	@ln -s . $(RPMNAME)
	tar -chf $@ --exclude $(RPMNAME)/$(RPMNAME) $(TAREXCLUDES) $(RPMNAME)/*
	@rm $(RPMNAME)

$(REDHAT.SOURCES)/$(TARBALL.GZ): $(REDHAT.SOURCES)/$(TARBALL)
	@gzip -f $^

$(REDHAT.SPECS)/$(SPECFILE): .buildenv-$(ROLL)/$(SPECFILE)
	@$(INSTALL) $^ $@

.PHONY: rpm-mkdirs
rpm-mkdirs:
	@echo
	@echo "::: rpm-mkdirs :::"
	@echo
	@if [ ! -d $(REDHAT.SOURCES) ]; then mkdir -p $(REDHAT.SOURCES); fi
	@if [ ! -d $(REDHAT.BUILD)  ]; then  mkdir -p $(REDHAT.BUILD); fi
	@if [ ! -d $(REDHAT.SPECS) ]; then   mkdir -p $(REDHAT.SPECS); fi
	@if [ ! -d $(REDHAT.RPMS) ]; then    mkdir -p $(REDHAT.RPMS); fi
	@if [ ! -d $(REDHAT.SRPMS) ]; then   mkdir -p $(REDHAT.SRPMS); fi


ifeq ($(MAKE.rpmflag),)
MAKE.rpmflag = -bb
endif

DEPENDENCIES += Makefile version.mk
ifeq ($(RPM.STRATEGY),src.rpm)
DEPENDENCIES += $(NAME)-$(VERSION)-$(RPM.RELEASE).src.rpm
endif
RPM.ARCH ?= $(ARCH)

ifneq ($(RPM.PACKAGE),)
RPM.NAME ?= $(NAME)-$(RPM.PACKAGE)-$(VERSION)-$(RELEASE).$(RPM.ARCH).rpm
else
RPM.NAME ?= $(NAME)-$(VERSION)-$(RELEASE).$(RPM.ARCH).rpm
endif

RPM.TARGET=$(REDHAT.ROOT)/RPMS/$(RPM.ARCH)/$(RPM.NAME)

# force depend.mk to be computed everytime
.PHONY: .buildenv-$(ROLL)/depend.mk

.buildenv-$(ROLL)/depend.mk: Makefile 
	@if [ ! -d .buildenv-$(ROLL) ]; then mkdir .buildenv-$(ROLL); fi
	@echo "#"               			>  $@
	@echo "# Do not edit"   			>> $@
	@echo "#"               			>> $@
	@echo                   			>> $@
ifneq ($(DEPENDS.RPMS),)
	@echo $(DEPENDS.RPMS) | gawk '			\
	BEGIN {	RS=" "; FS="\n"; }			\
	{						\
	cmd = "$(MAKE) -sC $(ROLLROOT)/src/" $$1 " dump-target"; \
	while ( ( cmd | getline result ) > 0 ) {	\
		n = split(result, a, "\n");		\
		for (i=1; i<n; i++)			\
			if (index(a[i], "/") == 1)	\
				print "DEPENDENCIES += " a[i];	\
	} 						\
	close(cmd);					\
	}'						>> $@
endif
ifneq ($(DEPENDS.DIRS),)
	@echo $(DEPENDS.DIRS) | gawk '			\
	BEGIN {	RS=" "; FS="\n"; }			\
	{						\
	cmd = "find " $$1 " -type f";			\
	while ( ( cmd | getline result ) > 0 ) {	\
		n = split(result, a, "\n");		\
		for (i=1; i<n; i++)			\
			print "DEPENDENCIES += " a[i];	\
	} 						\
	close(cmd);					\
	}'						>> $@
endif
ifneq ($(DEPENDS.FILES),)
	@echo $(DEPENDS.FILES) | gawk '			\
	BEGIN {	RS=" "; FS="\n"; }			\
	{						\
	print "DEPENDENCIES += " $$1;			\
	}'						>> $@
endif

include .buildenv-$(ROLL)/depend.mk

clean::
	@rm -f .buildenv-$(ROLL)/depend.mk

.PHONY: dump-target
dump-target:
	@echo $(RPM.TARGET)


ifneq ($(RPM.STRATEGY),custom)
ifneq ($(RPM.STRATEGY),copy)
ifeq ($(filter $(ROLL), $(ROLL.MEMBERSHIP)),$(ROLL))
.PHONY: rpm
rpm: $(RPM.TARGET)

ifndef __ROLLS_MK
.buildenv-$(ROLL)/install-rpm.mk: Makefile
	@if [ ! -d .buildenv-$(ROLL) ]; then mkdir .buildenv-$(ROLL); fi
	@echo "#"               			>  $@
	@echo "# Do not edit"   			>> $@
	@echo "#"               			>> $@
	@echo                   			>> $@
	@echo ".PHONY: install-rpm"			>> $@
	@echo "install-rpm: $(RPM.TARGET)"		>> $@
	@echo -e "\trpm -Uhv --force --nodeps $$<"	>> $@

include .buildenv-$(ROLL)/install-rpm.mk

clean::
	@rm -f .buildenv-$(ROLL)/install-rpm.mk
endif # __ROLLS_MK
else
rpm:
	@echo $(NAME) is not a member of $(ROLL)
endif # ($(filter $(ROLL), $(ROLL.MEMBERSHIP)),$(ROLL))
endif # ($(RPM.STRATEGY),copy)
endif # ($(RPM.STRATEGY),custom)


$(RPM.TARGET): $(DEPENDENCIES)
	@echo
	@echo ::: building rpm for $(NAME)-$(VERSION)-$(RELEASE) :::
	@echo
	@if [ "$(USERID)" != "0" ]; then				\
		echo;							\
		echo;							\
		echo ERROR - YOU MUST BE ROOT TO BUILD PACKAGES;	\
		echo;							\
		echo;							\
		exit 1;							\
	fi
	@echo
	@echo ::: cleaning before build :::
	@echo
	@$(MAKE) clean
	@echo
	@echo ::: creating $(HOME)/.rpmmacros :::
	@echo
	@rm -f $(HOME)/.rpmmacros
	@echo "%_topdir		$(REDHAT.ROOT)"	>  $(HOME)/.rpmmacros
	@echo "%buildroot	$(BUILDROOT)"	>> $(HOME)/.rpmmacros
	@echo "%_var		$(REDHAT.VAR)"	>> $(HOME)/.rpmmacros
	@echo "%debug_package	%{nil}"		>> $(HOME)/.rpmmacros
	@echo -e "%__os_install_post    \\" >> $(HOME)/.rpmmacros
	@echo -e "/usr/lib/rpm/brp-compress \\" >> $(HOME)/.rpmmacros
	@echo -e "%{!?__debug_package: \\" >> $(HOME)/.rpmmacros
	@echo -e "/usr/lib/rpm/brp-strip %{__strip} \\" >> $(HOME)/.rpmmacros
	@echo -e "/usr/lib/rpm/brp-strip-comment-note %{__strip} %{__objdump} \\" >> $(HOME)/.rpmmacros
	@echo -e "} \\" >> $(HOME)/.rpmmacros
	@echo -e "/usr/lib/rpm/brp-strip-static-archive %{__strip} \\" >> $(HOME)/.rpmmacros
	@echo -e "/usr/lib/rpm/brp-python-hardlink \\" >> $(HOME)/.rpmmacros
	@echo -e "%{nil}" >> $(HOME)/.rpmmacros
	@echo -e "$(RPM.MACROS.EXTRAS)"		>> $(HOME)/.rpmmacros
	@echo 
	@echo ::: creating redhat build directories :::
	@echo
	@if [ ! -d $(REDHAT.SOURCES) ]; then mkdir -p $(REDHAT.SOURCES); fi
	@if [ ! -d $(REDHAT.BUILD)  ]; then  mkdir -p $(REDHAT.BUILD); fi
	@if [ ! -d $(REDHAT.SPECS) ]; then   mkdir -p $(REDHAT.SPECS); fi
	@if [ ! -d $(REDHAT.RPMS) ]; then    mkdir -p $(REDHAT.RPMS); fi
	@if [ ! -d $(REDHAT.SRPMS) ]; then   mkdir -p $(REDHAT.SRPMS); fi
ifeq ($(RPM.STRATEGY),source)
	@echo
	@echo ::: creating source tarball :::
	@echo
	$(MAKE) pretar 
	#@if [ `basename $(CURDIR)` = usersguide ]; then $(MAKE) predoc; fi;
	@rm -rf $(RPMNAME)
	@ln -s . $(RPMNAME)
	tar -chf $(REDHAT.SOURCES)/$(TARBALL)				\
		--exclude $(RPMNAME)/$(RPMNAME)				\
		$(TAREXCLUDES)						\
		$(RPMNAME)/* $(RPMNAME)/.buildenv-$(ROLL)
	@rm $(RPMNAME)
	gzip -f $(REDHAT.SOURCES)/$(TARBALL)
	@echo
	@echo ::: building rpm from source :::
	@echo
	@$(MAKE) $(REDHAT.SPECS)/$(SPECFILE)
ifeq ($(RPM.OLDSTYLE),)
	@$(MAKE) .buildenv-$(ROLL)/$(NAME).spec.mk
endif
	rpmbuild $(MAKE.rpmflag) $(REDHAT.SPECS)/$(SPECFILE)
	@echo
	@echo ::: done :::
	@echo
ifndef __ROLLS_MK
	@echo If build completed you can now install the rpm using:
	@echo
	@echo make install-rpm
	@echo
endif
endif
ifeq ($(RPM.STRATEGY),src.rpm)
	@echo
	@echo ::: building rpm from src.rpm :::
	@echo
	rpmbuild --rebuild $(NAME)-$(VERSION)-$(RPM.RELEASE).src.rpm
	@echo
	@echo
	@echo ::: done :::
	@echo
	@echo If build completed you can now install the rpm using:
	@echo
	@echo make install-rpm
	@echo
endif
ifeq ($(RPM.STRATEGY),tar.rpm)
	@echo
	@echo ::: building rpm from tar.gz embedded specfile :::
	@echo
	rpmbuild -tb $(NAME)-$(VERSION).tar.gz;
	@echo
	@echo ::: done :::
	@echo
	@echo
	@echo If build completed you can now install the rpm using:
	@echo
	@echo make install-rpm
	@echo
endif

nuke:: clean
	@rm -f $(RPM.TARGET)


# pkg is an alias for rpm
pkg: rpm

clean::
	@rm -f $(REDHAT.SOURCES)/$(TARBALL)
	@rm -f $(REDHAT.SOURCES)/$(TARBALL.GZ)


# --------------------------------------------------------------------- #
# Build the spec file keeping the name,version,release in the Makefile 
# --------------------------------------------------------------------- #
PF = printf

ifeq ($(RPM.SUMMARY),)
rpm.summary = Summary: $(NAME)
else
rpm.summary = Summary: $(RPM.SUMMARY)
endif
ifeq ($(RPM.DESCRIPTION),)
rpm.description = $(NAME)
else
rpm.description = $(RPM.DESCRIPTION)
endif
ifneq ($(RPM.PREFIX),)
rpm.prefix = Prefix: $(RPM.PREFIX)
endif
ifneq ($(RPM.ARCH),)
rpm.arch = Buildarch: $(RPM.ARCH)
endif
ifneq ($(RPM.REQUIRES),)
rpm.requires = Requires: $(RPM.REQUIRES)
endif

ifneq ($(RPM.OLDSTYLE),)
#
# Old Style: User provides a .spec.in file
#
SEDSPEC = \
	-e 's%@PATH.CHILD@%$(PATH.CHILD)%g' \
	-e 's%@PATH.PARENT@%$(PATH.PARENT)%g' \
	-e 's%@NAME@%$(NAME)%g' \
	-e 's%@VERSION@%$(VERSION)%g' \
	-e 's%@RELEASE@%$(RELEASE)%g' \
	-e 's%@COPYRIGHT@%$(COPYRIGHT)%g' \
	-e 's%@VAR@%$(REDHAT.VAR)%g' \
	-e 's%^Vendor:$$%Vendor: $(VENDOR)%g' \
	-e 's%^Prefix:$$%$(rpm.prefix)%g' \
	-e 's%^Buildarch:$$%$(rpm.arch)%g' \
	-e 's%^Requires:$$%$(rpm.requires)%g'

.buildenv-$(ROLL)/$(NAME).spec: $(NAME).spec.in
	@if [ ! -d .buildenv-$(ROLL) ]; then mkdir .buildenv-$(ROLL); fi
	@$(SED) $(SEDSPEC) $^ > $@

else
#
# New Style: Rocks generates the .spec file
#
# The $(NAME).spec.mk file is called by the $(NAME).spec file to
# specify the build and install steps.  This makefile will then
# call make on the main Makefile.  This is done to minimize the
# spec files but more importantly to simplify debugging of RPM
# builds.  The side effect is we can no longer ship SRPMS since the
# spec files refer to developer home directories.  This means tagged
# CVS is the true source for all OSes.
#
ifneq ($(RPM.BUILDROOT),)
BUILDROOT = $(RPM.BUILDROOT)
else
BUILDROOT = $(shell pwd)/$(NAME).buildroot
endif

.buildenv-$(ROLL)/$(NAME).spec: .buildenv-$(ROLL)/$(NAME).spec.mk
	@if [ ! -d .buildenv-$(ROLL) ]; then mkdir .buildenv-$(ROLL); fi
	@$(PF) "$(rpm.summary)\n" > $@
	@$(PF) "Name: $(NAME)\n" >> $@
	@$(PF) "Version: $(VERSION)\n" >> $@
	@$(PF) "Release: $(RELEASE)\n" >> $@
	@$(PF) "License: " >>$@
	@if [ ! -f LICENSE ]; then			\
		$(PF) "$(COPYRIGHT)\n" >> $@;		\
	else						\
		cat LICENSE >> $@;			\
	fi
	@$(PF) "Vendor: $(VENDOR)\n" >> $@
	@$(PF) "Group: System Environment/Base\n" >> $@
	@$(PF) "VCS: $(shell git rev-parse --short HEAD)\n" >> $@
	@$(PF) "Source: $(NAME)-$(VERSION).tar.gz\n" >> $@
	@$(PF) "$(rpm.prefix)\n" >> $@
	@$(PF) "$(rpm.arch)\n" >> $@
	@$(PF) "$(rpm.requires)\n" >> $@
	@echo -e "$(RPM.EXTRAS)" >> $@
	@$(PF) "%%description\n" >> $@
	@if [ ! -f DESCRIPTION ]; then			\
		$(PF) "$(rpm.description)\n" >> $@;	\
	else						\
		cat DESCRIPTION >> $@;			\
	fi
	@if [ ! -z $(RPM.PACKAGE) ]; then \
	echo "" >> $@; \
	echo "%package $(RPM.PACKAGE)" >> $@; \
	echo "$(rpm.summary)" >> $@; \
	echo "Group: System Environment/Base" >> $@; \
	echo "%description $(RPM.PACKAGE)" >> $@; \
	echo "$(rpm.description)" >> $@; \
	fi
	@$(PF) "%%prep\n" >> $@
	@$(PF) "%%setup\n" >> $@
	@$(PF) "%%build\n" >> $@
	@$(PF) "$(PF) \"\\\n\\\n\\\n### build ###\\\n\\\n\\\n\"\n" >> $@
	@if [ -z "$(RPM.BUILDROOT)" ]; then \
	echo "BUILDROOT=$(BUILDROOT) make -f $(CURDIR)/.buildenv-$(ROLL)/$(NAME).spec.mk build" >> $@; \
	else \
	echo "BUILDROOT=$(BUILDROOT) make build" >> $@; \
	fi
	@$(PF) "%%install\n" >> $@
	@$(PF) "$(PF) \"\\\n\\\n\\\n### install ###\\\n\\\n\\\n\"\n" >> $@
	@if [ -z "$(RPM.BUILDROOT)" ]; then \
	echo "BUILDROOT=$(BUILDROOT) make -f $(CURDIR)/.buildenv-$(ROLL)/$(NAME).spec.mk install" >> $@; \
	else \
	echo "BUILDROOT=$(BUILDROOT) make install" >> $@; \
	fi
ifeq ($(RPM.FILESLIST),)
	@$(PF) "%%files $(RPM.PACKAGE)\n" >> $@
ifeq ($(RPM.PREFIX),)
	@$(PF) "/\n" >> $@
else
	@$(PF) "$(RPM.PREFIX)\n" >> $@
endif
else
	@$(PF) "%%files $(RPM.PACKAGE) -f $(RPM.FILESLIST)\n" >> $@

	@$(PF) "%%clean\n" >> $@
	@$(PF) "/bin/rm -rf $(RPM.FILESLIST)\n" >> $@
	@$(PF) "/bin/rm -rf $(BUILDROOT)" >> $@
endif
	@echo -e "$(RPM.FILE.EXTRAS)" >> $@

.buildenv-$(ROLL)/$(NAME).spec.mk:
	@if [ ! -d .buildenv-$(ROLL) ]; then mkdir .buildenv-$(ROLL); fi
	@$(PF) "# This file is called from the generated spec file.\n" > $@
	@$(PF) "# It can also be used to debug rpm building.\n" >> $@
	@$(PF) "# \tmake -f $@ build|install\n" >> $@
	@$(PF) "\n" >> $@
	@$(PF) "ifndef __RULES_MK\n" >> $@
	@$(PF) "build:\n" >> $@
	@$(PF) "\tmake ROOT=$(shell pwd)/$(NAME).buildroot build\n" >> $@
	@$(PF) "\n" >> $@
	@$(PF) "install:\n" >> $@
	@$(PF) "\tmake ROOT=$(shell pwd)/$(NAME).buildroot install\n" >> $@
	@$(PF) "\t$(STACKBUILD)/bin/genfilelist $(NAME) $(shell pwd)/$(NAME).buildroot > $(RPM.FILESLIST)\n" >> $@
	@$(PF) "endif\n" >> $@

clean::
	@rm -rf $(NAME).buildroot
endif

clean::
	@rm -f .buildenv-$(ROLL)/$(NAME).spec

endif	#__RULES_REDHAT_MK
