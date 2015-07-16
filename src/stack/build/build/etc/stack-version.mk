# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
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

ifndef __RELEASE_MK
__RELEASE_MK = yes

ifeq ($(ROLLVERSION),)
VERSION	= $(shell /opt/stack/bin/stack report version)
else
VERSION	= $(ROLLVERSION)
endif

STACK_VERSION = $(VERSION)

# A name, not a RPM release id. Added for flair. First releases named
# after well-known mountains.

RELEASE_NAME = 7.x
VERSION_NAME = "$(RELEASE_NAME)"

# The project name is used to identify to distribution.  The base 
# distribution is controlled by the "stack" projects.  If you want to
# build you own distribution and differentiate it from the parent
# distribution change this variable.  This is used by the anaconda
# loader as an attribute on the URL kickstart request line.

PROJECT_NAME = stack

# All docbook stuff include a publication date, let make this global
# right here.

PUBDATE = $(shell date +'%b %d %Y')
YEAR = $(shell date +'%Y')

rocks-copyright.txt:
	@rm -f $@
	@touch $@
	@echo '@Copyright@' >> $@
	@echo ' 				Rocks(r)' >> $@
	@echo ' 		         www.rocksclusters.org' >> $@
	@echo ' 		         version 5.4 (Maverick)' >> $@
	@echo ' ' >> $@
	@echo 'Copyright (c) 2000 - 2010 The Regents of the University of California.' >> $@
	@echo 'All rights reserved.	' >> $@
	@echo ' ' >> $@
	@echo 'Redistribution and use in source and binary forms, with or without' >> $@
	@echo 'modification, are permitted provided that the following conditions are' >> $@
	@echo 'met:' >> $@
	@echo ' ' >> $@
	@echo '1. Redistributions of source code must retain the above copyright' >> $@
	@echo 'notice, this list of conditions and the following disclaimer.' >> $@
	@echo ' ' >> $@
	@echo '2. Redistributions in binary form must reproduce the above copyright' >> $@
	@echo 'notice unmodified and in its entirety, this list of conditions and the' >> $@
	@echo 'following disclaimer in the documentation and/or other materials provided ' >> $@
	@echo 'with the distribution.' >> $@
	@echo ' ' >> $@
	@echo '3. All advertising and press materials, printed or electronic, mentioning' >> $@
	@echo 'features or use of this software must display the following acknowledgement: ' >> $@
	@echo ' ' >> $@
	@echo '	"This product includes software developed by the Rocks(r)' >> $@
	@echo '	Cluster Group at the San Diego Supercomputer Center at the' >> $@
	@echo '	University of California, San Diego and its contributors."' >> $@
	@echo '' >> $@
	@echo '4. Except as permitted for the purposes of acknowledgment in paragraph 3,' >> $@
	@echo 'neither the name or logo of this software nor the names of its' >> $@
	@echo 'authors may be used to endorse or promote products derived from this' >> $@
	@echo 'software without specific prior written permission.  The name of the' >> $@
	@echo 'software includes the following terms, and any derivatives thereof:' >> $@
	@echo '"Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of ' >> $@
	@echo 'the associated name, interested parties should contact Technology ' >> $@
	@echo 'Transfer & Intellectual Property Services, University of California, ' >> $@
	@echo 'San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, ' >> $@
	@echo 'Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu' >> $@
	@echo ' ' >> $@
	@echo 'THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''' >> $@
	@echo 'AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,' >> $@
	@echo 'THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR' >> $@
	@echo 'PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS' >> $@
	@echo 'BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR' >> $@
	@echo 'CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF' >> $@
	@echo 'SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR' >> $@
	@echo 'BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,' >> $@
	@echo 'WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE' >> $@
	@echo 'OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN' >> $@
	@echo 'IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.' >> $@
	@echo '@Copyright@' >> $@
	-cat $@ | grep -v "^@Copyright" | expand -- > $@.tmp
	-mv $@.tmp $@


clean::
	@rm -f rocks-copyright.txt

endif
