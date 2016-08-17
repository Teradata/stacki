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
                self.packages			= {}
		self.log			= '/var/log/stack-install.log'

                # We could set these elsewhere but this is the current
                # definition of the RedHat Generator.
                #
                # We used to do i386 (not anymore)

                self.setOS('redhat')
		self.setArch('x86_64')

	
	##
	## Parsing Section
	##

	def parse(self, xml_string):
		import cStringIO
		xml_buf = cStringIO.StringIO(xml_string)
		doc = xml.dom.ext.reader.Sax2.FromXmlStream(xml_buf)
		filter = stack.gen.MainNodeFilter(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		
		while node:
			if node.nodeName == 'profile':
				self.handle_profile(node)
			elif node.nodeName == 'main':
				child = iter.firstChild()
				while child:
					self.handle_mainChild(child)
					child = iter.nextSibling()

			node = iter.nextNode()
			
		filter = stack.gen.OtherNodeFilter(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		while node:
			if node.nodeName != 'profile':
				self.order(node)
                                try:
                                        fn = eval('self.handle_%s' % node.nodeName)
                                except AttributeError:
                                        fn = None
                                if fn:
                                        fn(node)
			node = iter.nextNode()


	# <profile>
	
	def handle_profile(self, node):
		# pull out the attr to handle generic conditionals
		# this replaces the old arch/os logic but still
		# supports the old syntax

		if node.attributes:
			attrs = node.attributes.getNamedItem((None, 'attrs'))
			if attrs:
				dict = eval(attrs.value)
				for (k,v) in dict.items():
					self.attrs[k] = v

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


	# <debug>
	
	def handle_debug(self, node):
                self.debugSection.append(self.getChildText(node), 
                                         self.getAttr(node, 'file'))

	
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

                # Once a package is disabled it stays disabled, so
                # only update the dictionary if the package doesn't
                # exist or is currently enabled.

                if rpm in self.packages:
                        (e, n) = self.packages[rpm]
                        if e:
                                self.packages[rpm] = (enabled, nodefile)
                else:
                        self.packages[rpm] = (enabled, nodefile)


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

                s = '%post'
                if interpreter:
                        s += ' --interpreter %s' % interpreter
                if arg and '--nochroot' in arg:
                        s += ' --log=/mnt/sysimage%s %s' % (self.log, arg)
                else:
                        s += ' --log=%s %s' % (self.log, arg)
                s += '\n%s' % self.getChildText(node)
                s += '%end'
			
                self.postSection.append(s, nodefile)


		
	# <boot>
	
	def handle_boot(self, node):
                nodefile	= self.getAttr(node, 'file')
                order		= self.getAttr(node, 'order')
                
                if not order:
                        order	= 'pre'

                s = '%%post --log=%s\n' % self.log
                s += "cat >> /etc/sysconfig/stack-%s << '__EOF__'\n" % order
		s += '%s' % self.getChildText(node)
                s += '__EOF__\n'
                s += '%end'

                self.bootSection[order].append(s, nodefile)


	def generate_main(self):
                return self.mainSection.generate()

	def generate_packages(self):

                section = stack.gen.ProfileSection()
                dict	= {}

                for (rpm, (enabled, nodefile)) in self.packages.items():
                        if not dict.has_key(nodefile):
                                dict[nodefile] = []
                        if not enabled:
                                rpm = '-%s' % rpm
                        dict[nodefile].append(rpm)
                
                for (nodefile, rpms) in dict.items():
                        rpms.sort()
                        for rpm in rpms:
                                section.append(rpm, nodefile)
                        
                list = []
		list.append('%packages --ignoremissing')
                for line in section.generate(cdata=False):
                        list.append(line)
		list.append('%end')
		return list


	def generate_pre(self):
                return self.preSection.generate()

	def generate_post(self):
                return self.postSection.generate()

	def generate_boot(self):
                section = stack.gen.ProfileSection()

		# check in/out all modified files

                s = '%%post --log=%s\n' % self.log
                s += "cat >> /etc/sysconfig/stack-pre << '__EOF__'\n"
		for (file, (owner, perms)) in self.rcsFiles.items():
			s += '%s' % self.rcsEnd(file, owner, perms)
                s += '\n__EOF__\n'
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

