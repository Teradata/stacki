# @copyright@
# @copyright@

ifndef __RULES_DEBIAN_MK
__RULES_DEBIAN_MK = yes

PKG.STRATEGY ?= source

USERID     = $(shell id -u)
INSTALL    = install
TARGET_PKG = deb
TAR        = tar
AWK	   = awk

ifndef ROLL.MEMBERSHIP
ROLL.MEMBERSHIP = $(ROLL)
endif


PALLET.ROOT = $(CURDIR)/$(ROLLROOT)/build-$(ROLL)-$(STACK)
PALLET.PKGS = $(PALLET.ROOT)/packages

ifeq ($(ARCH),armv7hl)
PKG.ARCH = armhf
else
ifeq ($(ARCH),x86_64)
PKG.ARCH    = amd64
else
PKG.ARCH    = $(ARCH)
endif
endif
PKG.NAME    = $(NAME)_$(VERSION)-$(RELEASE)_$(PKG.ARCH).deb
PKG.TARGET  = $(PALLET.PKGS)/$(PKG.NAME)


DEPENDENCIES += Makefile version.mk

.buildenv-$(ROLL)/depend.mk: Makefile 
	@if [ ! -d .buildenv-$(ROLL) ]; then mkdir .buildenv-$(ROLL); fi
	@echo "#"               			>  $@
	@echo "# Do not edit"   			>> $@
	@echo "#"               			>> $@
	@echo                   			>> $@
ifneq ($(DEPENDS.DIRS),)
	@echo $(DEPENDS.DIRS) | awk '			\
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
	@echo $(DEPENDS.FILES) | awk '			\
	BEGIN {	RS=" "; FS="\n"; }			\
	{						\
	print "DEPENDENCIES += " $$1;			\
	}'						>> $@
endif

include .buildenv-$(ROLL)/depend.mk

.PHONY: dump-target
dump-target:
	@echo $(PKG.TARGET)


ifneq ($(filter $(ROLL), $(ROLL.MEMBERSHIP)),$(ROLL))
pkg:
	@echo $(NAME) is not a member of $(ROLL)
else
ifneq ($(PKG.STRATEGY),custom)
pkg: $(PKG.TARGET)
endif
endif

rpm-mkdirs:

ifneq ($(PKG.STRATEGY),custom)
install-pkg: $(PKG.TARGET)
	dpkg -i $<
endif


$(PKG.TARGET): $(DEPENDENCIES)
	@echo
	@echo ::: building $(PKG.NAME) :::
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
	@echo ::: creating build directories :::
	@echo
	@if [ ! -d $(PALLET.PKGS) ]; then          mkdir -p $(PALLET.PKGS); fi
	@if [ ! -d .buildenv-$(ROLL)/build ]; then mkdir -p .buildenv-$(ROLL)/build; fi
ifeq ($(PKG.STRATEGY),source)
	@echo
	@echo ::: building rpm from source :::
	@echo
	$(MAKE) ROOT=$(CURDIR)/.buildenv-$(ROLL)/build build install
	fpm --input-type dir --output-type deb --name $(NAME) --version $(VERSION)-$(RELEASE)	\
		--chdir .buildenv-$(ROLL)/build 						\
		--package $(PALLET.PKGS)/$(NAME)_VERSION_ARCH.deb 				\
		--force --vendor=stacki
	@echo
	@echo ::: done :::
	@echo
	@echo If build completed you can now install the deb using:
	@echo
	@echo make install-pkg
	@echo
endif

nuke:: clean
	@rm -f $(PKG.TARGET)

endif	#__RULES_DEBIAN_MK
