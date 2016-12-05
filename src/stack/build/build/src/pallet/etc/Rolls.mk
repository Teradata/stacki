# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# Common Make rules for Rocks rolls.
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@

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
ISOSIZE			= 600

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
include $(ROLLSBUILD)/etc/roll-profile.mk

.PHONY: profile
profile: rpm

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
roll: $(TARGET_PKG)s roll-$(ROLL).xml rpm-mkdirs
	(								\
		cd build-$(ROLL)-$(STACK);				\
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

ifeq ($(ROLLS.API),4.0)
ifeq ($(OS),redhat)
ROLLS.OS=linux
endif
else
ifeq ($(ROLLS.OS),)
ROLLS.OS=$(OS)
endif
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
