#! /opt/stack/bin/python
# 
# @SI_Copyright@
#                             www.stacki.com
#                                  v3.0
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

import cStringIO
import string
import xml.dom.NodeFilter
import xml.dom.ext.reader.Sax2
import stack.cond
import stack.gen

class NodeFilter(stack.gen.NodeFilter):

	def acceptNode(self, node):
		if not node.attributes:
			return self.FILTER_ACCEPT
		
		cond    = self.getAttr(node, 'cond')
		arch    = self.getAttr(node, 'arch')
		osname  = self.getAttr(node, 'os')
		release = self.getAttr(node, 'release')
		expr    = stack.cond.CreateCondExpr(arch, osname, release, cond)

		if not stack.cond.EvalCondExpr(expr, self.attrs):
			return self.FILTER_SKIP

		return self.FILTER_ACCEPT
		
class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)	
		self.setOS('ubuntu')
		self.setArch('x86_64')
		
		self.mainSection        = stack.gen.ProfileSection()
		self.postSection        = stack.gen.ProfileSection()
		self.finishSection      = stack.gen.ProfileSection()

                self.tags        = {}
                self.doc         = None
                self.pruneList   = []
                self.replaceList = []

	##
	## Render xml for debugging purposes
	##
        def render(self, node):
                stream  = cStringIO.StringIO()
                xml.dom.ext.PrettyPrint(node, stream)
                s = stream.getvalue()
                stream.close()
                return s
	
	##
	## Parsing Section
	##
	def parse(self, xml_string):
		import cStringIO
		xml_buf = cStringIO.StringIO(xml_string)
		doc = xml.dom.ext.reader.Sax2.FromXmlStream(xml_buf)
		
		filter = NodeFilter(self.attrs, None)
		iter   = doc.createTreeWalker(doc, filter.SHOW_ELEMENT, filter, 0)
		node = iter.nextNode()
		
		while node:
			if node.localName != 'profile':
				self.order(node)

			if node.nodeName == 'main':
				child = iter.firstChild()
				while child:
					self.handle_mainChild(child)
					child = iter.nextSibling()
			else:
				name = string.join(node.nodeName.split(':'), '_')
				try:
					fn = eval('self.handle_%s' % name)
				except AttributeError:
					#print('handle_%s' %name)
					pass
			if fn:
				fn(node)
			node = iter.nextNode()

	def handle_early_command(self, node):
		nodefile = self.getAttr(node, 'file')
		txt = self.getChildText(node).strip()
		name = node.nodeName.split('-')
		self.mainSection.append('d-i %s/early_command string %s' % \
			(name[0], txt))

	def handle_mainChild(self, node):
		nodefile = self.getAttr(node, 'file')
		if 'tasksel' in node.nodeName:	
			self.mainSection.append('%s %s' % \
				(node.nodeName, self.getChildText(node)), nodefile)
		elif 'early_command' in node.nodeName:
			self.handle_early_command(node)
		else:
			self.mainSection.append('d-i %s/%s' % \
				(node.nodeName, self.getChildText(node)), nodefile)
	
	def handle_late_command(self, node):
		nodefile = self.getAttr(node, 'file')
		txt = self.getChildText(node)
		commands = txt.split(";")
		
		for (idx, command) in enumerate(commands):
			command = command.strip()
			if not command:
				continue
			
			if not self.postSection.snippets:
				self.postSection.append(
					'd-i preseed/%s string %s;\\' % \
					(node.nodeName.strip(), command), nodefile)
			elif idx < len(commands) - 2:
				self.postSection.append('%s;\\' % command, nodefile)
			else:
				self.postSection.append('%s' % command, nodefile)

	def handle_grub_installer(self, node):
		nodefile = self.getAttr(node, 'file')
		self.finishSection.append('d-i grub-installer/%s' % \
			self.getChildText(node), nodefile)

	def handle_finish_install(self, node):
		nodefile = self.getAttr(node, 'file')
		self.finishSection.append('d-i finish-install/%s' % \
			self.getChildText(node), nodefile)

	def handle_pre(self, node):
		pass

#	def handle_stack_post(self, node):
#		pass

        def handle_stack_post(self, node):
                if self.getProfileType() == 'shell':
                        nodefile        = self.getAttr(node, 'file')
                        interpreter     = self.getAttr(node, 'interpreter')
                        arg             = self.getAttr(node, 'arg')
                        section         = self.getChildText(node)
                        tmp             = tempfile.mktemp()

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
                else:
                        self.pruneList.append(node)

	def handle_package(self, node):
		pass
	
	def generate_main(self):
		return self.mainSection.generate()

	def generate_post(self):
		return self.postSection.generate()

	def generate_finish(self):
		return self.finishSection.generate()
