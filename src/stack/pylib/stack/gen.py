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
                        l.append('\t/opt/stack/bin/rcs -noriginal: %s;' % file)
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
		l.append('\t/opt/stack/bin/rcs -Nstack: %s;' % file)
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
			fn = eval('self.handle_main_%s' % node.nodeName)
                except AttributeError:
                        fn = None
                if fn:
                        fn(node)
                else:
			self.ks['main'].append(('%s %s' % (node.nodeName,
				self.getChildText(node)), roll, nodefile, color))


		
	def parseFile(self, node):
		attr = node.attributes

		if attr.getNamedItem((None, 'os')):
			OS = attr.getNamedItem((None, 'os')).value
			if OS != self.getOS():
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
                        p, f = os.path.split(fileName)
                        s    = 'if [ ! -e %s ]; then mkdir -p %s; fi\n' % (p, p)

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
                                try:
                                        fn = eval('self.handle_child_%s' % child.nodeName)
                                except AttributeError:
                                        fn = None
                                if fn:
                                        text += fn(child)
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
		for (roll, nodefile, color) in self.ks['order']:
                        list.append(nodefile)
		return list

	def generate_debug(self):
		list = []
		for text in self.ks['debug']:
			for line in string.split(text, '\n'):
				list.append('# %s' % line)
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

class MainNodeFilter(NodeFilter):

	def acceptNode(self, node):
	
		if node.nodeName in [ 'profile', 'main' ]:
			return self.FILTER_ACCEPT

                if not (node.parentNode and node.parentNode.nodeName == 'main'):
			return self.FILTER_SKIP

		if not self.isCorrectCond(node):
			return self.FILTER_SKIP

		return self.FILTER_ACCEPT


class OtherNodeFilter(NodeFilter):

	def acceptNode(self, node):

		if node.nodeName == 'profile':
			return self.FILTER_ACCEPT

                if node.nodeName in [ '#document', 'main' ]:
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

                # We could set these elsewhere but this is the current
                # definition of the RedHat Generator.
                #
                # We used to do i386 (not anymore)

                self.setOS('redhat')
		self.setArch('x86_64')


		self.rpm_context	= {}
		self.log = '/var/log/stack-install.log'

	
	##
	## Parsing Section
	##
	
	def parse(self, xml_string):
		import cStringIO
		xml_buf = cStringIO.StringIO(xml_string)
		doc = xml.dom.ext.reader.Sax2.FromXmlStream(xml_buf)
		filter = MainNodeFilter(self.attrs)
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
			
		filter = OtherNodeFilter(self.attrs)
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
		pre_attrs = {}
		# Collect arguments to the pre section
		for this_attr in ['interpreter', 'notify', 'arg', 'wait']:
			if attr.getNamedItem((None, this_attr)):
				pre_attrs[this_attr] = attr.getNamedItem((None, this_attr)).value
		self.ks['pre'].append((pre_attrs, self.getChildText(node), roll, nodefile, color))

	# <post>
	
	def handle_post(self, node):
		attr = node.attributes
		(roll, nodefile, color) = self.get_context(node)
		post_attrs = {}
		# Collect arguments to the post section
		for this_attr in ['interpreter', 'notify', 'arg', 'wait']:
			if attr.getNamedItem((None, this_attr)):
				post_attrs[this_attr] = attr.getNamedItem((None, this_attr)).value
		self.ks['post'].append((post_attrs, self.getChildText(node), roll, nodefile, color))
		
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

		for ks_pre_data in self.ks['pre']:
			args = ks_pre_data[0]
			text = ks_pre_data[1]
			roll = ks_pre_data[2]
			nodefile = ks_pre_data[3]
			color = ks_pre_data[4]
			log_line = '/tmp/ks-pre.log'
			pre_header = '%pre'
			# Add the interpreter, if applicable
			if 'interpreter' in args:
				pre_header += " --interpreter " + args['interpreter']
			# Assumes all args get added on to the logline
			if 'arg' in args:
				log_line = ' --log=/tmp/ks-pre.log %s' % args['arg']
			else:
				log_line = ' --log=%s' % self.log
			if 'wait' in args:
				# to be polite, send a notification that we're waiting
				notify_script = '/opt/stack/lib/python2.6/site-packages/stack/notify.py'
				wait_string = '\n%%pre\nchmod a+x %s\n' % notify_script
				waitfile = '/tmp/wait.txt'
				msg = 'waiting for %s in %s' % (waitfile, os.path.basename(nodefile))
				wait_string += '%s %s\n\n' % (notify_script, msg)
				wait_string += 'touch %s\n' % waitfile
				wait_string += 'while [ -f %s ]; do\n' % waitfile
				wait_string += '\tsleep 2;\ndone\n'
				wait_string += '%end\n'
				pre_list.append((wait_string, roll, nodefile, color))
			# if there's a notify argument, prepend it to text
			if 'notify' in args:
				msg = args['notify']
				# if notify='' --> just use the node.xml filename w/o extension
				if not msg:
					msg = os.path.splitext(os.path.basename(nodefile))[0]
				notify_script = '/opt/stack/lib/python2.6/site-packages/stack/notify.py'
				notify_cmd = '\n%%pre\nchmod a+x %s\n' % notify_script
				notify_cmd += '%s %s\n\n%%end\n\n' % (notify_script, msg)
				pre_list.append((notify_cmd, roll, nodefile, color))
			pre_list.append(('%s %s' % (pre_header, log_line), roll, nodefile, color))
			pre_list.append((text + '\n',roll, nodefile, color))
			pre_list.append(('%end'))
			
		return pre_list

	def generate_post(self):
		post_list = []
		post_list.append(('', None, None))

		for ks_post_data in self.ks['post']:
			args = ks_post_data[0]
			text = ks_post_data[1]
			roll = ks_post_data[2]
			nodefile = ks_post_data[3]
			color = ks_post_data[4]
			log_line = self.log
			post_header = '%post'
			# Add the interpreter, if applicable
			if 'interpreter' in args:
				post_header += " --interpreter " + args['interpreter']
			# Assumes all args get added on to the logline
			if 'arg' in args and  '--nochroot' in args['arg']:
				log_line = ' %s --log=/mnt/sysimage%s' % (args['arg'], self.log)
			else:
				log_line = ' --log=%s' % self.log
			if 'wait' in args:
				# to be polite, send a notification that we're waiting
				notify_script = '/opt/stack/lib/python2.6/site-packages/stack/notify.py'
				wait_string = '\n%%post --nochroot\nchmod a+x %s\n' % notify_script
				waitfile = '/tmp/wait.txt'
				msg = 'waiting for %s in %s' % (waitfile, os.path.basename(nodefile))
				wait_string += '%s %s\n\n' % (notify_script, msg)
				wait_string += 'touch %s\n' % waitfile
				wait_string += 'while [ -f %s ]; do\n' % waitfile
				wait_string += '\tsleep 2;\ndone\n'
				wait_string += '%end\n'
				post_list.append((wait_string, roll, nodefile, color))
			# if there's a notify argument, prepend the notification code to the text
			if 'notify' in args:
				msg = args['notify']
				# if notify='' --> just use the node.xml filename w/o extension
				if not msg:
					msg = os.path.splitext(os.path.basename(nodefile))[0]
				notify_script = '/opt/stack/lib/python2.6/site-packages/stack/notify.py'
				notify_cmd = '\n%%post --nochroot\nchmod a+x %s\n' % notify_script
				notify_cmd += '%s %s\n\n%%end\n\n' % (notify_script, msg)
				post_list.append((notify_cmd, roll, nodefile, color))
			post_list.append(('%s %s' % (post_header, log_line), roll, nodefile, color))
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

