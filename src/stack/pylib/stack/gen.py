#! /opt/stack/bin/python
# 
# @SI_Copyright@
#				stacki.com
#				   v4.0
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
#	 "This product includes software developed by StackIQ" 
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
#				Rocks(r)
#			 www.rocksclusters.org
#			 version 5.4 (Maverick)
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
#	"This product includes software developed by the Rocks(r)
#	Cluster Group at the San Diego Supercomputer Center at the
#	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".	 For licensing of 
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
from xml.sax import handler
import xml.dom.minidom
from stack.bool import *
import stack.cond
from stack.profile import StackNSURI, StackNSLabel
	
		
class ProfileSnippet:
	
	def __init__(self, text, source):
		self.source	= source
		self.text	= text

	def getText(self):
		return self.text

	def getSource(self):
		return self.source

class ProfileSection:

	def __init__(self):
		self.snippets = []

	def append(self, text, source=None):
		self.snippets.append(ProfileSnippet(text, source))
		return self

	def generate(self, cdata=True):
		prev = None
		open = False
		list = []

		if cdata:
			cdataStart = '<![CDATA['
			cdataEnd   = ']]>'
		else:
			cdataStart = ''
			cdataEnd   = ''

		for snippet in self.snippets:
			source = snippet.getSource()
			text   = snippet.getText()

			if not source:
				source = 'internal'

			if source != prev:
				if open:
					list.append('\t\t%s</subsection>' % cdataEnd)
				list.append('\t\t<subsection source="%s">%s' % 
					    (source, cdataStart))
				open = True
			list.append(snippet.getText())
			prev = source
		if open:
			list.append('\t\t%s</subsection>' % cdataEnd)
		return list


class PackageSet:

	def __init__(self):
		self.packages = {}

	def append(self, package, enabled=True, source=None):
		"""
		Add a package to the set, Once a package is disabled it stays
		disabled, so only update the dictionary if the package
		doesn't exist or is currently enabled.
		"""
		if package in self.packages:
			(e, n) = self.packages[package]
			if e:
				self.packages[package] = (enabled, source)
		else:
			self.packages[package] = (enabled, source)


	def getPackages(self):

		dict = { 'enabled': {}, 'disabled' : {} }

		for (package, (enabled, source)) in self.packages.items():
			if enabled:
				d = dict['enabled']
			else:
				d = dict['disabled']
			if not source in d:
				d[source] = []
			d[source].append(package)
		
		return dict

		

		
class Generator:
	"""Base class for various DOM based kickstart graph generators.
	The input to all Generators is assumed to be the XML output of KPP."""
	
	def __init__(self):
		self.attrs		= {}
		self.arch		= None
		self.os			= None
		self.profileType	= 'native'
		self.rcsFiles		= {}
		self.nodeFilesDict	= {}
		self.stackiSection	= ProfileSection()
		self.nodeFilesSection	= ProfileSection()
		self.debugSection	= ProfileSection()
		self.mainSection	= ProfileSection()
		self.log		= '/var/log/stack-install.log'

	def setArch(self, arch):
		self.arch = arch
		
	def getArch(self):
		return self.arch
	
	def setOS(self, osname):
		self.os = osname
		
	def getOS(self):
		return self.os

	def setProfileType(self, profileType):
		self.profileType = profileType
		
	def getProfileType(self):
		return self.profileType

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
			l.append('if [ -e /opt/stack/bin/rcs ]; then')
			l.append('\tif [ ! -f %s ]; then' % rcsfile)
			l.append('\t\tif [ ! -f %s ]; then' % file)
			l.append('\t\t\ttouch %s' % file)
			l.append('\t\tfi')
			l.append('\t\tif [ ! -d %s ]; then' % rcsdir)
			l.append('\t\t\tmkdir -m 700 %s' % rcsdir)
			l.append('\t\t\tchown 0:0 %s' % rcsdir)
			l.append('\t\tfi')
			l.append('\t\techo "original" | /opt/stack/bin/ci -q %s' % file)
			l.append('\t\t/opt/stack/bin/rcs -noriginal: %s' % file)
			l.append('\t\t/opt/stack/bin/co -q -f -l %s' % file)
			l.append('\tfi')
			if owner:
				l.append('\tchown %s %s' % (owner, rcsfile))
			l.append('fi')

		# If this is a subsequent file tag and the optional PERMS
		# or OWNER attributes are missing, use the previous value(s).
		
		if file in self.rcsFiles:
			(orig_owner, orig_perms) = self.rcsFiles[file]
			if not perms:
				perms = orig_perms
			if not owner:
				owner = orig_owner

		self.rcsFiles[file] = (owner, perms)
		
		l.append('')

		return '\n'.join(l)

	def rcsEnd(self, file, owner, perms):
		"""
		Run the final ci/co of a <file>.  The ownership of both the
		file and rcs file are changed to match the last requested
		owner in the file tag.	The perms of the file (not the file
		file) are also modified.

		The file is checked out locked, which is why we don't modify
		the perms of the RCS file itself.
		"""
		rcsdir	= os.path.join(os.path.dirname(file), 'RCS')
		rcsfile = '%s,v' % os.path.join(rcsdir, os.path.basename(file))
		l	= []

		l.append('if [ -e /opt/stack/bin/rcs ]; then')
		l.append('\tif [ -f %s ]; then' % file)
		l.append('\t\techo "stack" | /opt/stack/bin/ci -q %s' % file)
		l.append('\t\t/opt/stack/bin/rcs -Nstack: %s' % file)
		l.append('\t\t/opt/stack/bin/co -q -f -l %s' % file)
		l.append('\tfi')

		if owner:
			l.append('\tchown %s %s' % (owner, rcsfile))

		l.append('fi')

		if owner:
			l.append('chown %s %s' % (owner, file))
		if perms:
			l.append('chmod %s %s' % (perms, file))

		l.append('')

		return '\n'.join(l)

	
	def getAttr(self, node, attr, ns=StackNSURI):
		a = node.attributes.getNamedItemNS(ns, attr)
		if a:
			return a.value
		else:
			return ''
		
	def isCorrectCond(self, node):

		if not self.attrs or not node.nodeType == node.ELEMENT_NODE:
			return True

		arch	= self.getAttr(node, 'arch')
		osname	= self.getAttr(node, 'os')
		release = self.getAttr(node, 'release')
		cond	= self.getAttr(node, 'cond')

		expr = stack.cond.CreateCondExpr(arch, osname, release, cond)
		return stack.cond.EvalCondExpr(expr, self.attrs)

	
	def order(self, node):
		"""
		Stores the order of traversal of the nodes
		Useful for debugging.
		"""
		nodefile = self.getAttr(node, 'file')

		if nodefile and nodefile not in self.nodeFilesDict:
			self.nodeFilesDict[nodefile] = True
			self.nodeFilesSection.append(nodefile)
		

		
	# <*>
	#	<*> - tags that can go inside any other tags
	# </*>

	def getChildText(self, node):
		text = ''
		for child in node.childNodes:
			if child.nodeType == child.TEXT_NODE:
				text += child.nodeValue
			elif child.nodeType == child.CDATA_SECTION_NODE:
				text += child.nodeValue
			elif child.nodeType == child.ELEMENT_NODE:
				if self.isCorrectCond(child):
					if child.namespaceURI == 'http://www.stacki.com':
						fnname = 'stack_%s' % child.localName
					else:
						fnname = string.join(child.nodeName.split(':'), '_')
					try:
						fn = eval('self.handle_child_%s' % fnname)
					except AttributeError:
						fn = None
					if fn:
						text += fn(child)
		return text


	def traverse(self, node):
		terminal = False

		if not self.isCorrectCond(node):
			return
		if not node.nodeType == node.ELEMENT_NODE:
			return
		if not node.namespaceURI == StackNSURI:
			return

		# Lookup the handler and run it. If the handler
		# returns True we do NOT recurse further and assume
		# the handler already did this.

		try:
			fn = eval('self.handle_stack_%s' % node.localName)
		except AttributeError:
			fn = None
		if fn:
			if fn(node) == True:
				terminal = True
		if not terminal:
			for child in node.childNodes:
				self.traverse(child)

	def parse(self, xml_string):
		doc = xml.dom.minidom.parseString(xml_string)
		self.traverse(doc.getElementsByTagNameNS(StackNSURI, 'profile')[0])


	# <profile>
	
	def handle_stack_profile(self, node):
		# pull out the attr to handle generic conditionals
		# this replaces the old arch/os logic but still
		# supports the old syntax

		if node.attributes:
			attrs = node.attributes.getNamedItemNS(StackNSURI, 'attrs')
			if attrs:
				dict = eval(attrs.value)
				for (k,v) in dict.items():
					self.attrs[k] = v


	# <main>
	#	<*/>
	#	*
	# </main>

	def handle_stack_main(self, node):
		nodefile = self.getAttr(node, 'file')

		for child in node.childNodes:
			if not self.isCorrectCond(child):
				continue
			if child.nodeType == child.ELEMENT_NODE:
				try:
					fn = eval('self.handle_stack_main_%s' % child.localName)
				except AttributeError:
					fn = None
				if fn:
					text = fn(node)
				else:
					tagText	  = child.localName
					childText = self.getChildText(child)
				if childText:
					text = '%s %s' % (tagText, childText)
				else:
					text = '%s' % tagText
				self.mainSection.append(text, nodefile)
			else:
				self.mainSection.append(child.nodeValue, nodefile)
		return True

	# <*>
	#	<file>
	# </*>
	
	def handle_child_stack_file(self, node):

		fileName    = self.getAttr(node, 'name')
		fileMode    = self.getAttr(node, 'mode')
		fileOwner   = self.getAttr(node, 'owner')
		filePerms   = self.getAttr(node, 'perms')
		fileQuoting = self.getAttr(node, 'vars')
		fileCommand = self.getAttr(node, 'expr')
		fileRCS	    = self.getAttr(node, 'rcs')
		fileText    = self.getChildText(node)

		if not fileQuoting:
			fileQuoting = 'literal'
		if fileRCS:
			fileRCS = str2bool(fileRCS)
		else:
			fileRCS = True

		if fileName:
			p, f = os.path.split(fileName)
			s    = 'if [ ! -e %s ]; then mkdir -p %s; fi\n' % (p, p)

			if fileRCS:
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

			if fileOwner:
				s += 'chown %s %s\n' % (fileOwner, fileName)
			if filePerms:
				s += 'chmod %s %s\n' % (filePerms, fileName)
		return s
	

	# <stacki>

	def handle_stack_stacki(self, node):
		self.stackiSection.append(self.getChildText(node),
					  self.getAttr(node, 'file'))
		return True

	# <debug>
	
	def handle_stack_debug(self, node):
		self.debugSection.append(self.getChildText(node), 
					 self.getAttr(node, 'file'))
		return True
	
	##
	## Generator Section
	##
			
	def generate(self, section):
		"""Dump the requested section of the kickstart file.  If none 
		exists do nothing."""
		list = []
		try:
			f = getattr(self, "generate_%s" % section)
		except AttributeError:
			f = None
		if f:
			list += f()

		return list

	def generate_order(self):
		return self.nodeFilesSection.generate()

	def generate_stacki(self):
		return self.stackiSection.generate()

	def generate_debug(self):
		return self.debugSection.generate()


class ProfileHandler(handler.ContentHandler,
		     handler.DTDHandler,
		     handler.EntityResolver,
		     handler.ErrorHandler):

	def __init__(self):
		handler.ContentHandler.__init__(self)
		self.recording = False
		self.text      = ''
		self.chapters  = {}
		self.chapter   = None

	def startElement(self, name, attrs):
		if name == 'chapter':
			self.chapter   = self.chapters[attrs.get('name')] = []
			self.recording = True

	def endElement(self, name):
		if self.recording:
			self.chapter.append(self.text)
			self.text = ''

		if name == 'chapter':
			self.recording = False

	def characters(self, s):
		if self.recording:
			self.text += s

	def getChapter(self, chapter):
		doc = []
		if chapter in self.chapters:
			for text in self.chapters[chapter]:
				doc.append(text.strip())
		return doc




