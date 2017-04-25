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

node_files := $(wildcard *nodes/*.xml) $(wildcard *nodes/site.attrs) $(wildcard nodes/$(ROLL)/*.xml)
graph_dirs := $(wildcard graphs/*) $(wildcard graphs/*/$(ROLL))
graph_files := $(foreach dir,$(graph_dirs),$(wildcard $(dir)/*.xml))
site_nodes := $(wildcard site-nodes/*.xml)
screen_files := $(wildcard include/screens/*.py) $(wildcard include/$(ROLL)/screens/*.py)
javascript_files := $(wildcard include/javascript/*.js) $(wildcard include/$(ROLL)/javascript/*.js)


ifdef __RULES_REDHAT_MK
install_class_files := $(wildcard include/installclass/*.py) $(wildcard include/$(ROLL)/installclass/*.py)
install_classes_files := $(wildcard include/installclasses/*.py) $(wildcard include/$(ROLL)/installclasses/*.py)
applet_files := $(wildcard include/applets/*.py) $(wildcard include/$(ROLL)/applets/*.py)
endif

export PROFILE_DIR

$(graph_files)::
	sed \
		-e 's%<graph>%<graph roll="$(ROLL)">%g' \
		-e 's%[[:space:]]*<changelog>%<changelog><![CDATA[%g' \
		-e 's%[[:space:]]*</changelog>%]]></changelog>%g' \
		$@ > $(ROOT)/$(PROFILE_DIR)/graphs/default/$(@F)

# CDATA stuff goes here

$(node_files)::
	sed \
		-e 's%^<kickstart%<kickstart roll="$(ROLL)" color="$(COLOR)"%g' \
		-e 's%^<jumpstart%<jumpstart roll="$(ROLL)" color="$(COLOR)"%g' \
		-e 's%[[:space:]]*<changelog>%<changelog><![CDATA[%g' \
		-e 's%[[:space:]]*</changelog>%]]></changelog>%g' \
		$@ > $(ROOT)/$(PROFILE_DIR)/nodes/$(@F)

$(screen_files) $(install_class_files) $(install_classes_files) $(applet_files) $(javascript_files)::
	$(INSTALL) -m0644 $@ $(ROOT)/$(PROFILE_DIR)/$@

profile_dir::
	mkdir -p $(ROOT)/$(PROFILE_DIR)
	if [ -d graphs/default ]; then \
		( mkdir -p $(ROOT)/$(PROFILE_DIR)/graphs/default; ); fi
	if [ -d nodes ]; then \
		( mkdir -p $(ROOT)/$(PROFILE_DIR)/nodes; ); fi
	if [ -d site-nodes ]; then \
		( mkdir -p $(ROOT)/$(PROFILE_DIR)/site-nodes; ); fi
	if [ -d include/screens ]; then \
		( mkdir -p $(ROOT)/$(PROFILE_DIR)/include/screens; ) fi
	if [ -d include/installclass ]; then \
		( mkdir -p $(ROOT)/$(PROFILE_DIR)/include/installclass; ) fi
	if [ -d include/installclasses ]; then \
		( mkdir -p $(ROOT)/$(PROFILE_DIR)/include/installclasses; ) fi
	if [ -d include/applets ]; then \
		( mkdir -p $(ROOT)/$(PROFILE_DIR)/include/applets; ) fi
	if [ -d include/javascript ]; then \
		( mkdir -p $(ROOT)/$(PROFILE_DIR)/include/javascript; ) fi

build: roll-$(ROLL).xml

install:: profile_dir $(node_files) $(graph_files) $(screen_files) $(install_class_files) $(install_classes_files) $(applet_files) $(javascript_files)
	if [ -f roll-$(ROLL).xml ]; then \
		( $(INSTALL) -m0644 roll-$(ROLL).xml \
			$(ROOT)/$(PROFILE_DIR)/ ; ); fi

