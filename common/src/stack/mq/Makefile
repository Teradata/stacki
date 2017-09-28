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

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.DIRS	= daemons producers processors clients

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PY.STACK)/stack/mq/producers
	mkdir -p $(ROOT)/$(PY.STACK)/stack/mq/processors
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	mkdir -p $(ROOT)/etc/rc.d/init.d/
	# client
	$(INSTALL) -m 0755 clients/publish.py		$(ROOT)/$(PKGROOT)/bin/rmq-publish
	$(INSTALL) -m 0755 clients/channel-ctrl.py	$(ROOT)/$(PKGROOT)/bin/channel-ctrl
	# daemons
	$(INSTALL) -m 0755 daemons/producer.py		$(ROOT)/$(PKGROOT)/sbin/rmq-producer
	$(INSTALL) -m 0755 daemons/publisher.py		$(ROOT)/$(PKGROOT)/sbin/rmq-publisher
	$(INSTALL) -m 0755 daemons/shipper.py		$(ROOT)/$(PKGROOT)/sbin/rmq-shipper
	$(INSTALL) -m 0755 daemons/processor.py		$(ROOT)/$(PKGROOT)/sbin/rmq-processor
	# init files
	$(INSTALL) -m 0755 daemons/producer.init	$(ROOT)/etc/rc.d/init.d/rmq-producer
	$(INSTALL) -m 0755 daemons/publisher.init	$(ROOT)/etc/rc.d/init.d/rmq-publisher
	$(INSTALL) -m 0755 daemons/shipper.init		$(ROOT)/etc/rc.d/init.d/rmq-shipper
	$(INSTALL) -m 0755 daemons/processor.init	$(ROOT)/etc/rc.d/init.d/rmq-processor
	# producers / processors / pylib
	$(INSTALL) -m 0644 $(wildcard producers/*.py)	$(ROOT)/$(PY.STACK)/stack/mq/producers/
	$(INSTALL) -m 0644 $(wildcard processors/*.py)	$(ROOT)/$(PY.STACK)/stack/mq/processors/
	$(INSTALL) -m 0644 $(wildcard pylib/mq/*.py)	$(ROOT)/$(PY.STACK)/stack/mq/



