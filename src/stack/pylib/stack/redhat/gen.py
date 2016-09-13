#! /opt/stack/bin/python
# 
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

import string
import os
import tempfile
import xml.dom.ext.reader.Sax2
import stack.gen	
		

class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)
                self.preSection			= stack.gen.ProfileSection()
                self.postSection		= stack.gen.ProfileSection()
                self.bootSection		= {}
                self.bootSection['pre']		= stack.gen.ProfileSection()
                self.bootSection['post']	= stack.gen.ProfileSection()
                self.shellSection		= stack.gen.ProfileSection()
                self.packageSet			= stack.gen.PackageSet()

                # We could set these elsewhere but this is the current
                # definition of the RedHat Generator.
                #
                # We used to do i386 (not anymore)

                self.setOS('redhat')
		self.setArch('x86_64')

	
	# <main>
	#	<clearpart>
	# </main>
	
	def handle_main_clearpart(self, node):
		attr = node.attributes

		if attr.getNamedItem((None, 'partition')):
			arg = attr.getNamedItem((None, 'partition')).value
		else:
			arg = ''

		#
		# the web form sets the environment variable 'partition'
		# (although, we may find that it makes sense for other
		# sources to set it too).
		#
		try:
			os_arg = os.environ['partition']
		except:
			os_arg = ''

		if (arg == '') or (os_arg == '') or (arg == os_arg):
                        return 'clearpart %s' % self.getChildText(node)


	
	# <main>
	#	<lilo>
	# </main>
	
	def handle_main_lilo(self, node):
		return 'bootloader %s' % self.getChildText(node).strip()


	# <main>
	#	<langsupport>
	# </main>

	def handle_main_langsupport(self, node):
		return 'langsupport --default=%s' % self.getChildText(node).strip()


	# <package>

	def handle_package(self, node):
                nodefile = self.getAttr(node, 'file')
		rpm      = self.getChildText(node).strip()
                type     = self.getAttr(node, 'type')

                if self.getAttr(node, 'disable'):
                        enabled = False
                else:
                        enabled = True

                if type == 'meta':
                        rpm = '@%s' % rpm

                self.packageSet.append(rpm, enabled, nodefile)


	# <pre>
	
	def handle_pre(self, node):
                nodefile	= self.getAttr(node, 'file')
                interpreter	= self.getAttr(node, 'interpreter')
                arg		= self.getAttr(node, 'arg')

                s = '%pre'
                if interpreter:
                        s += ' --interpreter %s' % interpreter
                s += ' --log=%s %s' % (self.log, arg)
                s += '\n%s' % self.getChildText(node)
                s += '%end'
			
                self.preSection.append(s, nodefile)


	# <post>
	
	def handle_post(self, node):
                nodefile	= self.getAttr(node, 'file')
                interpreter	= self.getAttr(node, 'interpreter')
                arg		= self.getAttr(node, 'arg')

                if self.getProfileType() == 'native':
                        s = '%post'
                        if interpreter:
                                s += ' --interpreter %s' % interpreter
                        if arg and '--nochroot' in arg:
                                s += ' --log=/mnt/sysimage%s %s' % (self.log, arg)
                        else:
                                s += ' --log=%s %s' % (self.log, arg)
                        s += '\n%s' % self.getChildText(node)
                        s += '%end'

                elif self.getProfileType() == 'shell':

                        section = self.getChildText(node)
                        tmp     = tempfile.mktemp()

                        if interpreter:
                                script  = 'cat > %s << "__EOF_%s__"\n' % (tmp, tmp)
                                script += '#! %s\n\n' % interpreter
                                script += section
                                script += '__EOF_%s__\n\n' % tmp
                                script += 'chmod +x %s\n' % tmp
                                script += '%s\n' % tmp
                        elif arg and '--nochroot' in arg:
                                # just ignore all the --nochroot stuff
                                script = ''
                        else:
                                script = section
			
                self.postSection.append(script, nodefile)


		
	# <boot>
	
	def handle_boot(self, node):
                nodefile	= self.getAttr(node, 'file')
                order		= self.getAttr(node, 'order')
                
                if not order:
                        order = 'pre'
                
                s = ''

                if self.getProfileType() == 'native':
                        s = '%%post --log=%s\n' % self.log

                s += "cat >> /etc/sysconfig/stack-%s << '__EOF__'\n" % order
		s += '%s' % self.getChildText(node)
                s += '__EOF__\n'

                if self.getProfileType() == 'native':
                        s += '%end'

                self.bootSection[order].append(s, nodefile)


	def generate_main(self):
                return self.mainSection.generate()

	def generate_packages(self):
                dict	 = self.packageSet.getPackages()
                enabled  = dict['enabled']
                disabled = dict['disabled']
                section  = stack.gen.ProfileSection()

                if self.getProfileType() == 'native':
                        section.append('%packages --ignoremissing')
                        for (nodefile, rpms) in enabled.items():
                                rpms.sort()
                                for rpm in rpms:
                                        section.append(rpm, nodefile)

                        for (nodefile, rpms) in disabled.items():
                                rpms.sort()
                                for rpm in rpms:
                                        section.append('-%s' % rpm, nodefile)
                        section.append('%end')
                elif self.getProfileType() == 'shell':
                        for (nodefile, rpms) in enabled.items():
                                rpms.sort()
                                for rpm in rpms:
                                        section.append('yum install -y %s' % rpm, nodefile)
                        
                return section.generate(cdata=False)


	def generate_pre(self):
                return self.preSection.generate()

	def generate_post(self):
                return self.postSection.generate()

	def generate_boot(self):
                section = stack.gen.ProfileSection()

		# check in/out all modified files
                s = ''
                if self.getProfileType() == 'native':
                        s += '%%post --log=%s\n' % self.log
                s += "cat >> /etc/sysconfig/stack-pre << '__EOF__'\n"
		for (file, (owner, perms)) in self.rcsFiles.items():
			s += '%s' % self.rcsEnd(file, owner, perms)
                s += '\n__EOF__\n'
                if self.getProfileType() == 'native':
                        s += '%end'
		section.append(s)

		list = []

		# Boot PRE

                for line in section.generate():
                        list.append(line)
                for line in self.bootSection['pre'].generate():
                        list.append(line)


		# Boot POST
		
                for line in self.bootSection['post'].generate():
                        list.append(line)

		
		return list

        def generate_shell(self):
                for line in self.generate_packages():
                        print line

