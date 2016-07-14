# @SI_Copyright@
#                               stacki.com
#                                  v3.2
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

ifndef __CCRULES_MK
__CCRULES_MK = yes

##
## Set default ROLL name
##
-include version.mk

##
## Load CCCommon.mk and Rocks Rules.mk
##
include $(STACKBUILD)/etc/CCCommon.mk
include $(STACKBUILD)/etc/Rules.mk


##
## Docbook changes for Clustercorp
##

ifeq ($(SUMMARY_COMPATIBLE),)
SUMMARY_COMPATIBLE	= $(VERSION)
endif

SUMMARY_MAINTAINER	= &stackiq;
SUMMARY_ARCHITECTURE	= $(ARCH)

entities.sgml::
	echo "<!ENTITY rollname-l \"&roll-$(ROLL)-l;\">" >> $@
	echo "<!ENTITY rollname-s \"&roll-$(ROLL)-s;\">" >> $@
	echo "<!ENTITY rollname-d \"&roll-$(ROLL)-d;\">" >> $@
	echo "<!ENTITY rollname \"&roll-$(ROLL);\">" >> $@
	for platform in $(ROLL_PLATFORMS); do \
		echo "<!ENTITY platform-$$platform \"<entry>yes</entry>\">" >> $@; \
	done
	cat $(DOCROOT)/rocksplus-general-entities.sgml >> $@
	for roll in $(ROLL_REQUIRES); do \
		echo "<!ENTITY overview-$$roll-depend \"<row><entry namest="req">&roll-$$roll-s;</entry></row>\">" >> $@; \
	done
	for roll in $(ROLL_CONFLICTS); do \
		echo "<!ENTITY overview-$$roll-depend \"<row><entry namest="con">&roll-$$roll-s;</entry></row>\">" >> $@; \
	done
	cat $(DOCROOT)/rocksplus-overview-entities.sgml >> $@

predoc::
	if [ ! -f ./rocks+.dsl ]; then cp $(DOCROOT)/rocks+.dsl .; fi;
	if [ ! -f ./rocksplus.css ]; then cp $(DOCROOT)/rocksplus.css .; fi;

predoctemplates::
	cp $(DOCROOT)/rocksplus-overview.sgml \
		roll-rocksplus-overview.sgml
	cp $(DOCROOT)/rocksplus-overview-entities.sgml \
		roll-rocksplus-overview-entities.sgml
	cp $(DOCROOT)/rocksplus-copyright.sgml \
		roll-rocksplus-copyright.sgml
	[ -d $(DOCROOT)/images/ ] &&	\
	for i in $(DOCROOT)/images/*.png; do	\
		b=`basename $$i`;		\
		[ ! -f images/roll-$$b ] && 	\
			cp $$i images/roll-$$b;	\
		done;

clean::
	@rm -f rocks+.dsl
	@rm -f rocksplus.css


endif # __CCRULES_MK
