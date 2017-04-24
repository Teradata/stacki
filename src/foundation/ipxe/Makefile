# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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

PKGROOT		= /opt/stack/ipxe
ROLLROOT	= ../../..
DEPENDS.FILES	= $(NAME)-$(VERSION)-$(RELEASE).tgz

include $(STACKBUILD)/etc/CCRules.mk


bootstrap:
	yum install -y xz-devel
	$(MAKE) install-rpm

refresh:
	git clone git://git.ipxe.org/ipxe.git
	(cd ipxe ; git archive --format=tgz HEAD > \
		../ipxe-$(VERSION)-`date +%Y%m%d`.tgz)

build:
	mkdir $(NAME)
	(cd $(NAME) ; tar zvfx ../$(NAME)-$(VERSION)-$(RELEASE).tgz)
	(								\
		cd $(NAME)/src ;					\
		awk -f ../../config.awk config/general.h > general.h ;	\
		mv general.h config/ ;					\
		$(MAKE) everything ; 					\
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(								\
		cd $(NAME)/src ;					\
		rm -rf bin*/deps bin*/*.o bin*/*.tmp bin*/*.map bin*/.*;\
		cp -r bin* $(ROOT)/$(PKGROOT);				\
	)

tgz:
	mkdir ipxe-src
	(cd ipxe-src ; \
		git clone git://git.ipxe.org/ipxe.git)
	(cd ipxe-src/ipxe ; \
		git archive -o ../../$(NAME)-$(VERSION)-$(RELEASE).tgz HEAD)

clean::
	rm -rf $(NAME)

