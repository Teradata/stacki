# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# Common Make rules for Rocks rolls.
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

ifndef __ROLLS_MK
__ROLLS_MK = yes

# --------------------------------------------------------------------- #
# Initialize some variables for pallet building
# --------------------------------------------------------------------- #

ROLLS.API	= 6.0.2

BOOTABLE		= 0
ADDCOMPS		= 0
INCLUDE_PROFILES	= 1
INCLUDE_GRAPHS  	= 1
INCLUDE_RPMS		= 1

TAREXCLUDES	= --exclude src --exclude 'build-*'

# --------------------------------------------------------------------- #
# Include the standard build Rules.mk
# --------------------------------------------------------------------- #

include version.mk

STACKBUILD = $(ROLLSBUILD)/../..

ifeq ($(ROLL),)
ROLL = $(notdir $(CURDIR))
else
NAME     = roll-$(ROLL)
endif
export ROLL

include $(STACKBUILD)/etc/Rules.mk

# When running at the roll directory, make roll as
# the default target
.DEFAULT_GOAL = roll

MKISOFSFLAGS = "-b isolinux/isolinux.bin -c isolinux/boot.cat \
	-no-emul-boot -boot-load-size 4 -boot-info-table"

ifeq ($(ROLLS),)
WITHROLLS = 0
else
WITHROLLS = "$(ROLLS)"
endif


# --------------------------------------------------------------------- #
# support for building rolls
# --------------------------------------------------------------------- #

.PHONY: roll
preroll::
roll: rpm-mkdirs preroll $(TARGET_PKG)s roll-$(ROLL).xml 
	(								\
		cd $(REDHAT.ROOT);					\
		rm -rf disk*;						\
		env GNUPGHOME=$(STACKBUILD.ABSOLUTE)/../.gnupg		\
			Kickstart_Lang=$(KICKSTART_LANG)		\
			Kickstart_Langsupport=$(KICKSTART_LANGSUPPORT)	\
			/opt/stack/bin/stack create pallet ../roll-$(ROLL).xml;\
	)

.PHONY: reroll
reroll: roll

pretar:: roll-$(ROLL).xml 

.PHONY: $(TARGET_PKG)s
$(TARGET_PKG)s: 
	@echo 
	@echo ::: building src packages :::
	@echo
	@if [ -d src ]; then (cd src; $(MAKE) BG="$(MAKEBG)" $(TARGET_PKG)); fi

clean::
	rm -rf comps 

# --------------------------------------------------------------------- #
# Build to pallet.xml file
# --------------------------------------------------------------------- #

ifeq ($(ROLLS.OS),)
ROLLS.OS=$(OS)
endif

ifeq ($(ISOSIZE),)
ISOSIZE=0
endif

roll-$(ROLL).xml:
	@echo "<roll name=\"$(ROLL)\" interface=\"$(ROLLS.API)\">" > $@
	@echo "<timestamp time=\"$(TIME)\""\
		"date=\"$(DATE)\" tz=\"$(TZ)\"/>" >> $@	
	@echo "<color edge=\"$(COLOR)\" node=\"$(COLOR)\"/>" >> $@
	@echo "<info version=\"$(VERSION)\" release=\"$(RELEASE)\""\
		"arch=\"$(ARCH)\" os=\"$(ROLLS.OS)\"/>" >> $@
	@echo "<iso maxsize=\"$(ISOSIZE)\" addcomps=\"$(ADDCOMPS)\" bootable=\"$(BOOTABLE)\""\
		"mkisofs=\"$(MKISOFSFLAGS)\"/>" >> $@
	@echo "<$(TARGET_PKG) rolls=\"$(WITHROLLS)\""\
		"bin=\"$(INCLUDE_RPMS)\" src=\"0\"/>" >> $@
	@echo "<author name=\"$(USER)\""\
		"host=\"$(shell /bin/hostname)\"/>" >> $@
	@echo "<gitstatus><![CDATA["				>> $@
	-git status 2>/dev/null					>> $@
	@echo "]]></gitstatus>"					>> $@
	@echo "<gitlog>"					>> $@
	-git log 2>/dev/null | awk '/^commit / { print $$2; }'	>> $@
	@echo "</gitlog>"					>> $@
	@echo "</roll>" >> $@

clean::
	rm -f roll-$(ROLL).xml


clean::
	rm -rf anaconda anaconda-runtime
	rm -rf rpmdb

endif
