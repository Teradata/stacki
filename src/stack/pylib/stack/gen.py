#! /opt/stack/bin/python
# 
# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
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

import string
import types
import sys
import os
import time
import xml.dom.NodeFilter
import xml.dom.ext.reader.Sax2
import stack.js
import stack.cond
	
		

class NodeFilter(xml.dom.NodeFilter.NodeFilter):

	def __init__(self, attrs):
		self.attrs = attrs

	def isCorrectCond(self, node):

		attr = node.attributes.getNamedItem((None, 'arch'))
		if attr:
			arch = attr.value
		else:
			arch = None

		attr = node.attributes.getNamedItem((None, 'os'))
		if attr:
			os = attr.value
			if os == 'linux':
				os = 'redhat'
		else:
			os = None

		attr = node.attributes.getNamedItem((None, 'release'))
		if attr:
			release = attr.value
		else:
			release = None

		attr = node.attributes.getNamedItem((None, 'cond'))
		if attr:
			cond = attr.value
		else:
			cond = None

		expr = stack.cond.CreateCondExpr(arch, os, release, cond)
		return stack.cond.EvalCondExpr(expr, self.attrs)

		
class Generator:
	"""Base class for various DOM based kickstart graph generators.
	The input to all Generators is assumed to be the XML output of KPP."""
	
	def __init__(self):
		self.attrs	= {}
		self.arch	= None
		self.rcsFiles	= {}

	def setArch(self, arch):
		self.arch = arch
		
	def getArch(self):
		return self.arch
	
	def setOS(self, osname):
		self.os = osname
		
	def getOS(self):
		return self.os

	def isDisabled(self, node):
		return node.attributes.getNamedItem((None, 'disable'))

	def isMeta(self, node):
		attr  = node.attributes
		type  = attr.getNamedItem((None, 'type'))
		if type:
			type = type.value
		else:
			type = 'rpm'
		if type  == 'meta':
			return 1
		return 0
	
	def rcsBegin(self, file, owner, perms):
		"""
		If the is the first time we've seen a file ci/co it.  Otherwise
		just track the ownership and perms from the <file> tag .
		"""
		
		rcsdir	= os.path.join(os.path.dirname(file), 'RCS')
		rcsfile = '%s,v' % os.path.join(rcsdir, os.path.basename(file))
		l	= []

		l.append('')

		if file not in self.rcsFiles:
			l.append('if [ ! -f %s ]; then' % rcsfile)
			l.append('\tif [ ! -f %s ]; then' % file)
			l.append('\t\ttouch %s;' % file)
			l.append('\tfi')
			l.append('\tif [ ! -d %s ]; then' % rcsdir)
			l.append('\t\tmkdir -m 700 %s' % rcsdir)
			l.append('\t\tchown 0:0 %s' % rcsdir)
		 	l.append('\tfi;')
			l.append('\techo "original" | /opt/stack/bin/ci -q %s;' %
			 	file)
			l.append('\t/opt/stack/bin/co -q -f -l %s;' % file)
			l.append('fi')

		# If this is a subsequent file tag and the optional PERMS
		# or OWNER attributes are missing, use the previous value(s).
		
		if self.rcsFiles.has_key(file):
			(orig_owner, orig_perms) = self.rcsFiles[file]
			if not perms:
				perms = orig_perms
			if not owner:
				owner = orig_owner

		self.rcsFiles[file] = (owner, perms)
		
		if owner:
			l.append('chown %s %s' % (owner, file))
			l.append('chown %s %s' % (owner, rcsfile))

		if perms:
			l.append('chmod %s %s' % (perms, file))

		l.append('')

		return string.join(l, '\n')

	def rcsEnd(self, file, owner, perms):
		"""
		Run the final ci/co of a <file>.  The ownership of both the
		file and rcs file are changed to match the last requested
		owner in the file tag.  The perms of the file (not the file
		file) are also modified.

		The file is checked out locked, which is why we don't modify
		the perms of the RCS file itself.
		"""
		rcsdir	= os.path.join(os.path.dirname(file), 'RCS')
		rcsfile = '%s,v' % os.path.join(rcsdir, os.path.basename(file))
		l	= []

		l.append('')
		l.append('if [ -f %s ]; then' % file)
		l.append('\techo "stack" | /opt/stack/bin/ci -q %s;' % file)
		l.append('\t/opt/stack/bin/co -q -f -l %s;' % file)
		l.append('fi')		

		if owner:
			l.append('chown %s %s' % (owner, file))
			l.append('chown %s %s' % (owner, rcsfile))

		if perms:
			l.append('chmod %s %s' % (perms, file))

		return string.join(l, '\n')

	
	def order(self, node):
		"""
		Stores the order of traversal of the nodes
		Useful for debugging.
		"""
		roll, nodefile, color = self.get_context(node)
		if (roll, nodefile, color) not in self.ks['order']:
			self.ks['order'].append((roll, nodefile, color))
		
	def handle_mainChild(self, node):
		attr = node.attributes
		roll, nodefile, color = self.get_context(node)
		try:
			eval('self.handle_main_%s(node)' % node.nodeName)
		except AttributeError:
			self.ks['main'].append(('%s %s' % (node.nodeName,
				self.getChildText(node)), roll, nodefile, color))

		
	def parseFile(self, node):
		attr = node.attributes

		if attr.getNamedItem((None, 'os')):
			os = attr.getNamedItem((None, 'os')).value
			if os != self.getOS():
				return ''

		if attr.getNamedItem((None, 'name')):
			fileName = attr.getNamedItem((None, 'name')).value
		else:
			fileName = ''

		if attr.getNamedItem((None, 'mode')):
			fileMode = attr.getNamedItem((None, 'mode')).value
		else:
			fileMode = 'create'

		if attr.getNamedItem((None, 'owner')):
			fileOwner = attr.getNamedItem((None, 'owner')).value
		else:
			fileOwner = ''

		if attr.getNamedItem((None, 'perms')):
			filePerms = attr.getNamedItem((None, 'perms')).value
		else:
			filePerms = ''

		if attr.getNamedItem((None, 'vars')):
			fileQuoting = attr.getNamedItem((None, 'vars')).value
		else:
			fileQuoting = 'literal'

		if attr.getNamedItem((None, 'expr')):
			fileCommand = attr.getNamedItem((None, 'expr')).value
		else:
			fileCommand = None

		# Have the ability to turn off/on RCS checkins
		if attr.getNamedItem((None, 'rcs')):
			t = attr.getNamedItem((None, 'rcs')).value.lower()
			if t == 'false' or t == 'off':
				rcs = False
		else:
			rcs = True

		fileText = self.getChildText(node)

		if fileName:

			s = ''
			if rcs:
				s += self.rcsBegin(fileName, fileOwner, filePerms)

			if fileMode == 'append':
				gt = '>>'
			else:
				gt = '>'

			if fileCommand:
				s += '%s %s %s\n' % (fileCommand, gt, fileName)
			if not fileText:
				s += 'touch %s\n' % fileName
			else:
				if fileQuoting == 'expanded':
					eof = "EOF"
				else:
					eof = "'EOF'"

				s += "cat %s %s << %s" % (gt, fileName, eof)
				if fileText[0] != '\n':
					s += '\n'
				s += fileText
				if fileText[-1] != '\n':
					s += '\n'
				s += 'EOF\n'

			# If RCS is disabled, we still need to have support
			# for changing permissions, and owners.
			if not rcs:
				if fileOwner:
					s += 'chown %s %s\n' % (fileOwner, fileName)
				if filePerms:
					s += 'chmod %s %s\n' % (filePerms, fileName)
		return s
	
	# <*>
	#	<*> - tags that can go inside any other tags
	# </*>

	def getChildText(self, node):
		text = ''
		for child in node.childNodes:
			if child.nodeType == child.TEXT_NODE:
				text += child.nodeValue
			elif child.nodeType == child.ELEMENT_NODE:
				text += eval('self.handle_child_%s(child)' \
					% (child.nodeName))
		return text

	
	# <*>
	#	<file>
	# </*>
	
	def handle_child_file(self, node):
		return self.parseFile(node)

	##
	## Generator Section
	##
			
	def generate(self, section, annotation=False):
		"""Dump the requested section of the kickstart file.  If none 
		exists do nothing."""
		list = []
		try:
			f = getattr(self, "generate_%s" % section)
		except AttributeError:
			f = None
		if f:
			list += f()

		return self.annotate(list, annotation)

	def generate_order(self):
		list = []
		list.append('#')
		list.append('# Node Traversal Order')
		list.append('#')
		for (roll, nodefile, color) in self.ks['order']:
			list.append(('# %s (%s)' % (nodefile, roll),
				roll, nodefile, color))
		list.append('#')
		return list

	def generate_debug(self):
		list = []
		list.append('#')
		list.append('# Debugging Information')
		list.append('#')
		for text in self.ks['debug']:
			for line in string.split(text, '\n'):
				list.append('# %s' % line)
		list.append('#')
		return list

	def annotate(self, l, annotation=False):
		o = []
		if annotation:
			for line in l:
				if type(line) == str or \
					type(line) == unicode:
					o.append([line, None, 'Internal', None])
				else:
					o.append(list(line))
		else:
			for line in l:
				if type(line) == tuple:
					o.append(line[0])
				else:
					o.append(line)
		return o

class MainNodeFilter_redhat(NodeFilter):

	def acceptNode(self, node):
	
		if node.nodeName in [ 'kickstart', 'main' ]:
			return self.FILTER_ACCEPT

                if not (node.parentNode and node.parentNode.nodeName == 'main'):
			return self.FILTER_SKIP

		if not self.isCorrectCond(node):
			return self.FILTER_SKIP

		return self.FILTER_ACCEPT


class OtherNodeFilter_redhat(NodeFilter):
	def acceptNode(self, node):

		if node.nodeName == 'kickstart':
			return self.FILTER_ACCEPT
			
		if node.nodeName not in [
			'attributes', 
			'debug',
			'description',
			'package',
			'pre', 
			'post',
			'boot'
			]:
			return self.FILTER_SKIP
			
		if not self.isCorrectCond(node):
			return self.FILTER_SKIP

		return self.FILTER_ACCEPT


class Generator_redhat(Generator):

	def __init__(self):
		Generator.__init__(self)	
		self.ks                 = {}
		self.ks['order']	= []
		self.ks['debug']	= []
		self.ks['main']         = []
		self.ks['rpms-on']	= []
		self.ks['rpms-off']	= []
		self.ks['pre' ]         = []
		self.ks['post']         = []
		self.ks['boot-pre']	= []
		self.ks['boot-post']	= []

		self.rpm_context	= {}
		self.log = '/var/log/stack-install.log'

	
	##
	## Parsing Section
	##
	
	def parse(self, xml_string):
		import cStringIO
		xml_buf = cStringIO.StringIO(xml_string)
		doc = xml.dom.ext.reader.Sax2.FromXmlStream(xml_buf)
		filter = MainNodeFilter_redhat(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		
		while node:
			if node.nodeName == 'kickstart':
				self.handle_kickstart(node)
			elif node.nodeName == 'main':
				child = iter.firstChild()
				while child:
					self.handle_mainChild(child)
					child = iter.nextSibling()

			node = iter.nextNode()
			
		filter = OtherNodeFilter_redhat(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		while node:
			if node.nodeName != 'kickstart':
				self.order(node)
				eval('self.handle_%s(node)' % (node.nodeName))
			node = iter.nextNode()


	# <kickstart>
	
	def handle_kickstart(self, node):
		# pull out the attr to handle generic conditionals
		# this replaces the old arch/os logic but still
		# supports the old syntax

		if node.attributes:
			attrs = node.attributes.getNamedItem((None, 'attrs'))
			if attrs:
				dict = eval(attrs.value)
				for (k,v) in dict.items():
					self.attrs[k] = v

	def get_context(self, node):
		# This function returns the rollname,
		# and nodefile of the node currently being
		# processed
		attr = node.attributes
		roll = None
		nodefile = None
		color = None
		if attr.getNamedItem((None, 'roll')):
			roll = attr.getNamedItem((None, 'roll')).value
		if attr.getNamedItem((None, 'file')):
			nodefile = attr.getNamedItem((None, 'file')).value
		if attr.getNamedItem((None, 'color')):
			color = attr.getNamedItem((None, 'color')).value
		return (roll, nodefile, color)
	# <main>
	#	<clearpart>
	# </main>
	
	def handle_main_clearpart(self, node):
		(roll, nodefile, color) = self.get_context(node)
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

		clearpart = self.getChildText(node)

		if (arg == '') or (os_arg == '') or (arg == os_arg):
			self.ks['main'].append(('clearpart %s' % clearpart,
				roll, nodefile, color))

	
	# <main>
	#	<lilo>
	# </main>
	
	def handle_main_lilo(self, node):
		(roll, nodefile, color) = self.get_context(node)
		self.ks['main'].append(('bootloader %s' %
			self.getChildText(node), roll, nodefile, color))
		return


	# <main>
	#	<bootloader>
	# </main>

	def handle_main_bootloader(self, node):
		(roll, nodefile, color) = self.get_context(node)
		self.ks['main'].append(('bootloader %s' %
			self.getChildText(node), roll, nodefile, color))
		return

	# <main>
	#	<lang>
	# </main>

	def handle_main_lang(self, node):
		(roll, nodefile, color) = self.get_context(node)
		self.ks['main'].append(('lang %s' %
			self.getChildText(node), roll, nodefile, color))
		return

	# <main>
	#	<langsupport>
	# </main>

	def handle_main_langsupport(self, node):
		(roll, nodefile, color) = self.get_context(node)
		self.ks['main'].append(('langsupport --default=%s' %
			self.getChildText(node).strip(),
			roll, nodefile, color))

		return

	# <main>
	#	<volgroup>
	# </main>

	def handle_main_volgroup(self, node):
		(roll, nodefile, color) = self.get_context(node)
		self.ks['main'].append(('volgroup %s' %
			self.getChildText(node).strip(),
			roll, nodefile, color))

		return

	# <main>
	#	<logvol>
	# </main>

	def handle_main_logvol(self, node):
		(roll, nodefile, color) = self.get_context(node)
		self.ks['main'].append(('logvol %s' %
			self.getChildText(node).strip(),
			roll, nodefile, color))
		return

	# <debug>
	
	def handle_debug(self, node):
		(roll, nodefile, color) = self.get_context(node)
		self.ks['debug'].append((self.getChildText(node), roll, nodefile, color))
	
	# <package>
	def handle_package(self, node):
		rpm = self.getChildText(node).strip()
		if self.isDisabled(node):
			key = 'rpms-off'
		else:
			key = 'rpms-on'

		if self.isMeta(node):
			rpm = '@' + rpm	


		# if the RPM is to be turned off, only add if it is not 
		# in the on list.

		if key == 'rpms-off':
			if rpm not in self.ks['rpms-on']:
				self.ks[key].append(rpm)

		# if RPM is turned on, make sure it is not in the off list

		if key == 'rpms-on':
			self.ks[key].append(rpm)

			if rpm in self.ks['rpms-off']:
				self.ks['rpms-off'].remove(rpm)

		self.rpm_context[rpm] = self.get_context(node)

	# <pre>
	
	def handle_pre(self, node):
		attr = node.attributes
		(roll, nodefile, color) = self.get_context(node)
		# Parse the interpreter attribute
		if attr.getNamedItem((None, 'interpreter')):
			interpreter = '--interpreter ' + \
				attr.getNamedItem((None, 'interpreter')).value
		else:
			interpreter = ''
		# Parse any additional arguments to the interpreter
		# or to the post section
		if attr.getNamedItem((None, 'arg')):
			arg = attr.getNamedItem((None, 'arg')).value
		else:
			arg = ''
		list = []
		list.append(string.strip(string.join([interpreter, arg])))
		list.append(self.getChildText(node))
		self.ks['pre'].append((list, roll, nodefile, color))

	# <post>
	
	def handle_post(self, node):
		attr = node.attributes
		(roll, nodefile, color) = self.get_context(node)
		# Parse the interpreter attribute
		if attr.getNamedItem((None, 'interpreter')):
			interpreter = '--interpreter ' + \
				attr.getNamedItem((None, 'interpreter')).value
		else:
			interpreter = ''
		# Parse any additional arguments to the interpreter
		# or to the post section
		if attr.getNamedItem((None, 'arg')):
			arg = attr.getNamedItem((None, 'arg')).value
		else:
			arg = ''
		list = []
		# Add the interpreter and args to the %post line
		list.append(string.strip(string.join([interpreter, arg])))
		list.append(self.getChildText(node))
		self.ks['post'].append((list, roll, nodefile, color))
		
	# <boot>
	
	def handle_boot(self, node):
		(roll, nodefile, color) = self.get_context(node)
		attr = node.attributes
		if attr.getNamedItem((None, 'order')):
			order = attr.getNamedItem((None, 'order')).value
		else:
			order = 'pre'

		self.ks['boot-%s' % order].append(
			(self.getChildText(node), roll, nodefile, color))


	def generate_main(self):
		list = []
		list.append('')
		list += self.ks['main']
		return list

	def generate_packages(self):
		list = []
		list.append('%packages --ignoremissing')
		self.ks['rpms-on'].sort()
		for e in self.ks['rpms-on']:
			if self.rpm_context.has_key(e):
				(roll, nodefile, color) = self.rpm_context[e]
			else:
				(roll, nodefile, color) = (none, none, none)
			list.append((e, roll, nodefile, color))
		self.ks['rpms-off'].sort()
		for e in self.ks['rpms-off']:
			if self.rpm_context.has_key(e):
				(roll, nodefile, color) = self.rpm_context[e]
			else:
				(roll, nodefile, color) = (none, none, none)
			list.append(('-'+ e, roll, nodefile, color))
		list.append('%end')
		return list

	def generate_pre(self):
		pre_list = []
		pre_list.append('')

		for list in self.ks['pre']:
			(args, text) = list[0][0], list[0][1]
			roll = list[1]
			nodefile = list[2]
			color = list[3]
			pre_list.append(('%%pre --log=/tmp/ks-pre.log %s' %
				args, roll, nodefile, color))
			pre_list.append((text + '\n',roll, nodefile, color))
			pre_list.append(('%end'))
			
		return pre_list

	def generate_post(self):
		post_list = []
		post_list.append(('', None, None))

		for list in self.ks['post']:
			(args, text) = list[0][0], list[0][1]
			roll = list[1]
			nodefile = list[2]
			color = list[3]
			log = self.log
			try:
				i = args.index('--nochroot')
				if i >= 0:
					log = '/mnt/sysimage/%s' % self.log
			except:
				pass
			post_list.append(('%%post --log=%s %s' %
				(log, args), roll, nodefile, color))
			post_list.append((text + '\n',roll, nodefile, color))
			post_list.append(('%end'))
			
		return post_list


	def generate_boot(self):
		list = []
		list.append('')
		list.append('%%post --log=%s' % self.log)
		
		# Boot PRE
		#	- check in/out all modified files
		#	- write the <boot order="pre"> text
		
		list.append('')
		list.append("cat >> /etc/sysconfig/stack-pre << '__EOF__'")

		for (file, (owner, perms)) in self.rcsFiles.items():
			s = self.rcsEnd(file, owner, perms)
			list.append(s)

		for l in self.ks['boot-pre']:
			list.append(l)

		list.append('__EOF__')

		# Boot POST
		#	- write the <boot order="post"> text
		
		list.append('')
		list.append("cat >> /etc/sysconfig/stack-post << '__EOF__'")

		for l in self.ks['boot-post']:
			list.append(l)

		list.append('__EOF__')
		list.append('')

		list.append('%end')
		
		return list


		
class MainNodeFilter_sunos(NodeFilter):
	"""
	This class either accepts or reject tags
	from the node XML files. All tags are under
	the <main>*</main> tags.
	Each and every one of these tags needs to
	have a handler for them in the Generator
	class.
	"""
	def acceptNode(self, node):
		if node.nodeName == 'jumpstart':
			return self.FILTER_ACCEPT

		if node.nodeName not in [
			'main', 	# <main><*></main>
			'clearpart', 	# Clears the disk partitions
			'url', 		# URL to download all the packages from
			'part', 	# Partition information
			'size',
			'filesys',
			'slice',
			'locale',
			'timezone',
			'timeserver',
			'terminal',
			'name_service',
			'domain_name',
			'name_server',
			'nfs4_domain',
			'search',
			'rootpw', 	# root password
			'network',	# specify network configuration
			'interface',	# network interface
			'hostname',	# hostname
			'ip_address',	# IP Address
			'netmask',	# Netmask information
			'default_route',# Default Gateway
			'dhcp',		# to DHCP or not to DHCP
			'protocol_ipv6',# to IPv6 or not to IPv6
			'display',	# Display config
			'monitor',	# Monitor config
			'keyboard',	# Keyboard Config
			'pointer',	# Mouse config
			'security_policy', # Security config
			'auto_reg',	# Auto Registration
			'type',	# Auto Registration
			]:
			return self.FILTER_SKIP
			
		if not self.isCorrectCond(node):
			return self.FILTER_SKIP
	
		return self.FILTER_ACCEPT



class OtherNodeFilter_sunos(NodeFilter):
	"""
	This class accepts tags that define the
	pre section, post section and the packages
	section in the node XML files. The handlers
	for these are present in the Generator class.
	"""
	def acceptNode(self, node):
		if node.nodeName == 'jumpstart':
			return self.FILTER_ACCEPT

		if node.nodeName not in [
			'cluster',
			'package',
			'patch',
			'pre',
			'post',
			]:
			return self.FILTER_SKIP

		if not self.isCorrectCond(node):
			return self.FILTER_SKIP
			
		return self.FILTER_ACCEPT
		
		
class Generator_sunos(Generator):
	"""
	Handles all the XML tags that are acceptable
	and generates a jumpstart compatible output
	"""
	def __init__(self):
		Generator.__init__(self)
		self.ks = {}
		self.ks['main']		= []
		self.ks['url']		= ''
		self.ks['order']	= [] # Order of traversal
		self.ks['sysidcfg']	= [] # The Main section
		self.ks['part']		= [] # Partitioning
		self.ks['profile']	= [] # Misc. Profile Information
		self.ks['pkg_on']	= [] # Selected Packages
		self.ks['pkg_off']	= [] # Deselected Packages
		self.ks['pkgcl_on']	= [] # Selected Package Clusters
		self.ks['pkgcl_off']	= [] # Deselected Package Clusters
		self.ks['patch']	= [] # List of patches
		self.ks['begin']	= [] # Begin Section
		self.ks['finish']	= [] # Finish Section
		self.ks['service_on']	= [] # Enabled Services section
		self.ks['service_off']	= [] # Disabled Services section
		self.finish_section	= 0  # Iterator. This counts up for
					     # every post section that's
					     # encountered
					     
		self.service_instances	= {}
						

	def parse(self, xml_string):
		"""
		Creates an XML tree representation of the XML string,
		decompiles it, and parses the string.
		"""
		import cStringIO
		xml_buf = cStringIO.StringIO(xml_string)
		doc = xml.dom.ext.reader.Sax2.FromXmlStream(xml_buf)
		filter = MainNodeFilter_sunos(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		
		while node:
			if node.nodeName == 'jumpstart':
				self.handle_jumpstart(node)
			elif node.nodeName == 'main':
				child = iter.firstChild()
				while child:
					self.handle_mainChild(child)
					child = iter.nextSibling()
					
			elif node.nodeName in [
				'name_service',
				'network',
				'auto_reg',
				]:
				f = getattr(self, "handle_%s" % node.nodeName)
				f(node, iter)

			node = iter.nextNode()

		filter = OtherNodeFilter_sunos(self.attrs)
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		while node:
			if node.nodeName != 'jumpstart':
				self.order(node)
				eval('self.handle_%s(node)' % (node.nodeName))
			node = iter.nextNode()

	# <jumpstart>
	
	def handle_jumpstart(self, node):
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
		self.ks['part'][0:0] = ['fdisk\trootdisk\tsolaris\tall']

	# <main>
	#	<url>
	# </main>
	
	def handle_main_url(self, node):
		self.ks['url'] = self.getChildText(node).strip()
	
	# <main>
	#	<rootpw>
	# </main>
	
	def handle_main_rootpw(self, node):
		self.ks['sysidcfg'].append("root_password=%s" %
			self.getChildText(node).strip())

	# <main>
	#	<locale>
	# </main>
	
	def handle_main_locale(self, node):
		self.ks['sysidcfg'].append("system_locale=%s" %
			self.getChildText(node).strip())

	# <main>
	#	<timezone>
	# </main>

	def handle_main_timezone(self, node):
		self.ks['sysidcfg'].append("timezone=%s" %
			self.getChildText(node).strip())

	# <main>
	#	<timeserver>
	# </main>

	def handle_main_timeserver(self, node):
		self.ks['sysidcfg'].append("timeserver=%s" %
			self.getChildText(node).strip())

	# <main>
	#	<nfs4_domain>
	# </main>

	def handle_main_nfs4_domain(self, node):
		self.ks['sysidcfg'].append("nfs4_domain=%s" %
			self.getChildText(node).strip())


	# <name_service>
	
	def handle_name_service(self, node, iter):
		dns = {}
		child = iter.firstChild()
		while child:
			dns[child.nodeName] = self.getChildText(child).strip()
			child = iter.nextSibling()
		self.ks['sysidcfg'].append("name_service=DNS {")
		for i in dns:
			self.ks['sysidcfg'].append('\t%s=%s' % (i, dns[i]))
		self.ks['sysidcfg'].append('}')
			
	
	# <auto_registration>
	def handle_auto_reg(self, node, iter):
		auto_reg = {}
		child = iter.firstChild()
		while child:
			auto_reg[child.nodeName] = self.getChildText(child).strip()
			child = iter.nextSibling()
		if not auto_reg.has_key('type'):
			self.ks['sysidcfg'].append('auto_reg=disable')
			return
		auto_reg_type = auto_reg.pop('type')
		if auto_reg_type in ['disable', 'none']:
			self.ks['sysidcfg'].append("auto_reg=%s" % auto_reg_type)
			return
		self.ks['sysidcfg'].append('auto_reg=%s {')
		for i in auto_reg:
			self.ks['sysidcfg'].append('\t%s=%s' % (i,auto_reg[i]))
		self.ks['sysidcfg'].append('}')
		
	# <main>
	#	<security_policy>
	# </main>
	
	def handle_main_security_policy(self, node):
		self.ks['sysidcfg'].append("security_policy=%s" %
			self.getChildText(node).strip())
	
	# <main>
	#	<display>
	# </main>
	
	def handle_main_display(self, node):
		self.ks['sysidcfg'].append("display=%s" %
			self.getChildText(node).strip())

	# <main>
	#	<monitor>
	# </main>
	
	def handle_main_monitor(self, node):
		self.ks['sysidcfg'].append("monitor=%s" %
			self.getChildText(node).strip())

	# <main>
	#	<keyboard>
	# </main>
	
	def handle_main_keyboard(self, node):
		self.ks['sysidcfg'].append("keyboard=%s" %
			self.getChildText(node).strip())

	# <main>
	#	<pointer>
	# </main>
	
	def handle_main_pointer(self, node):
		self.ks['sysidcfg'].append("pointer=%s" %
			self.getChildText(node).strip())
		

	# <*>
	#	<service>
	# </*>
	
	def handle_child_service(self, node):
		# Handle the <service> tags that enable
		# or disable services in Solaris
		
		# Get name and enabled flags
		attr = node.attributes
		name = None
		enabled = 'true'
		instance = 'default'
		if attr.getNamedItem((None, 'name')):
			name = attr.getNamedItem((None, 'name')).value
		# If there's no name return
		if not name:
			return ''

		if attr.getNamedItem((None, 'instance')):
			instance = attr.getNamedItem((None, 'instance')).value

		# populate the correct list, depending on
		# whether the service is enabled or disabled.
		if attr.getNamedItem((None, 'enabled')):
			enabled = attr.getNamedItem((None, 'enabled')).value
		if enabled == 'no' or enabled == 'false':
			enabled = 'false'
		else:
			enabled='true'

		if not self.service_instances.has_key(name):
			self.service_instances[name] = []
		self.service_instances[name].append((instance,enabled))
		# This is only to placate the getChildText
		# function. There's no need to return anything, as
		# a separate list is being populated to be used
		# later.
		return ''

	# <network>
	
	def handle_network(self, node, iter):
		net = {}
		dhcp = 0
		child = iter.firstChild()
		while child :
			if child.nodeName =='dhcp':
				dhcp = 1
			else:
				net[child.nodeName] = self.getChildText(child).strip()
			child = iter.nextSibling()
		if not net.has_key('interface'):
			net['interface'] = 'PRIMARY'
		self.ks['sysidcfg'].append("network_interface=%s{" %
			net.pop('interface'))
		if dhcp == 1:
			self.ks['sysidcfg'].append("\t\tdhcp")
		for i in net:
			self.ks['sysidcfg'].append("\t\t%s=%s" % (i, net[i]))
		self.ks['sysidcfg'].append("}")


	# <package>
	
	def handle_package(self, node):
		attr = node.attributes
		if self.isMeta(node):
			key = "pkgcl"
		else:
			key = "pkg"

		if self.isDisabled(node):
			key = key + "_off"
		else:
			key = key + "_on"

		self.ks[key].append(self.getChildText(node).strip())
		
	# patch
	def handle_patch(self, node):
		attr = node.attributes
		self.ks['patch'].append(self.getChildText(node))
	# <pre>
		
	def handle_pre(self, node):
		self.ks['begin'].append(self.getChildText(node))

	# <post>
	
	def handle_post(self, node):
		"""Function works in an interesting way. On solaris the post
		sections are executed in the installer environment rather than
		in the installed environment. So the way we do it is to write
		a script for every post section, with the correct interpreter
		and execute it with a chroot command.
		"""
		attr = node.attributes
		# By default we always want to chroot, unless
		# otherwise specified
		if attr.getNamedItem((None, 'chroot')):
			chroot = attr.getNamedItem((None, 'chroot')).value
		else:
			chroot = 'yes'

		# By default, the interpreter is always /bin/sh, unless
		# otherwise specified.
		if attr.getNamedItem((None, 'interpreter')):
			interpreter = attr.getNamedItem((None,
				'interpreter')).value
		else:
			interpreter = '/bin/sh'

		# The args that are supplied are for the command that
		# you want to run, and not to the installer section.
		if attr.getNamedItem((None, 'arg')):
			arg = attr.getNamedItem((None, 'arg')).value
		else:
			arg = ''

		list = []
		if chroot == 'yes':
			list.append("cat > /a/tmp/post_section_%d << '__eof__'"
					% self.finish_section)
			list.append("#!%s" % interpreter)
			list.append(self.getChildText(node))
			list.append("__eof__")
			list.append("chmod a+rx /a/tmp/post_section_%d"
					% self.finish_section)
			list.append("chroot /a /tmp/post_section_%d %s"
					% (self.finish_section, arg))
		else:
			if interpreter is not '/bin/sh':
				list.append("cat > /tmp/post_section_%d "
					"<< '__eof__'"
					% self.finish_section)
				list.append("#!%s" % interpreter)
				list.append(self.getChildText(node))
				list.append("__eof__")
				list.append("chmod a+rx /tmp/post_section_%d"
					% self.finish_section)
				list.append("%s /tmp/post_section_%d"
					% (interpreter, self.finish_section))
			
			else:
				list.append(self.getChildText(node))

		self.finish_section = self.finish_section+1
		self.ks['finish'] += list

	def generate(self, section):
		"""Function generates the requested section
		of the jumpstart file"""
		
		list = []
		
		f = getattr(self, 'generate_%s' % section )
		list += f()
		return list


	def generate_begin(self):
		""" Generates the pre installation scripts"""
		list = []
		list += self.ks['begin']
		return list

	def generate_finish(self):
		list = []
		list += self.generate_order()
		list += self.ks['finish']

		# Generate and add the services section to the finish
		# script. 
		list += self.generate_services()
		# And we're done
		
		return list

	def generate_profile(self):
		if self.ks['url'] != '':
			location = self.ks['url']
		else:
			location = "local_file\t/cdrom"
		list = []
		list.append("# Installation Type")
		list.append("install_type\tinitial_install")
		list.append("\n")
		list.append("# System Type")
		list.append("system_type\tstandalone")
		list.append("\n")
		list.append("# Profile Information")
		list.append("\n")
		list += self.ks['profile']
		list.append("# Partition Information")
		list += self.ks['part']
		list.append("\n")
		list.append("# Packages Section")
		for i in self.ks['pkgcl_on']:
			list.append('cluster\t%s' % i)
		for i in self.ks['pkgcl_off']:
			list.append('cluster\t%s\tdelete' % i)
		for i in self.ks['pkg_on']:
			list.append('package\t%s\tadd' % i)
		for i in self.ks['pkg_off']:
			list.append('package\t%s\tdelete' % i)
		if len(self.ks['patch']) > 0:
			patch_list = string.join(self.ks['patch'],',')
			list.append('patch %s local_file /cdrom/Solaris_10/Patches' % patch_list)

		return list
		
	def generate_sysidcfg(self):
		list = []
		list += self.ks['sysidcfg']
		return list

	def generate_rules(self):
		list = []
		list.append("any\t-\tbegin\tprofile\tfinish")
		return list

	def generate_services(self):

		# Generates an XML file with a list of 
		# all enabled and disabled services. This
		# is going to be used when assembling services
		# on compute nodes.
		# The way to do this is to copy the service manifest
		# xml file to /var/svc/manifest/ which should be done by
		# an explicit cp command in the post section. Then enable
		# these services by adding them to the site.xml command
		# on the target machine.

		if len(self.service_instances) == 0:
			return []
		list= []

		list.append("cat > /a/var/svc/profile/site.xml << '_xml_eof_'")
		# XML Headers, and doctype
		list.append("<?xml version='1.0'?>")
		list.append("<!DOCTYPE service_bundle SYSTEM "
			"'/usr/share/lib/xml/dtd/service_bundle.dtd.1'>")

		# Start service bundle
		list.append("<service_bundle type='profile' name='site'"
			"\n\txmlns:xi='http://www.w3.org/2001/XInclude' >")

		for i in self.service_instances.keys():
			list.append("\t<service name='%s' version='1' type='service'>" % i)
			for j in self.service_instances[i]:
				list.append("\t\t<instance name='%s' enabled='%s'/>" \
						% (j[0], j[1]))
			list.append("\t</service>")

		# End Service bundle
		list.append("</service_bundle>")
		list.append('_xml_eof_')

		return list
