#! /opt/stack/bin/python
# 
# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
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
		self.packageSet		= PackageSet()
		self.log		= '/var/log/stack-install.log'
		self.doc                = None
		self.root		= None

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


	def debug(self, msg, node):
		self.debugSection.append(msg, 
					 self.getAttr(node, 'stack:file'))
	
	
	def getAttr(self, node, attr, consume=False):
		a = node.attributes.getNamedItem(attr)
		if a:
			if consume:
				node.removeAttribute(attr)
			return a.value
		else:
			return ''
		
	
	def parse(self, xml_string):
		self.doc  = xml.dom.minidom.parseString(xml_string)
		self.root = self.doc.getElementsByTagName('stack:profile')[0]
		conds     = [ ]
		expanded  = [ ]

		for step in [ 'setup',		# load the attributes
			      'prune',		# remove failed conds
			      'expand',		# expand file tags
			      'pre',		# pre step for subclasses
			      'main',		# main loop for subclasses
			      'post' ]:		# post step for subclasses
			self.traverse(step, self.root)



	def traverse(self, step, node):
		return self._traverse(step, node)

	def _traverse(self, step, node):

		if not node.nodeType == node.ELEMENT_NODE:
			return

		ns  = node.prefix
		tag = node.localName

		# Lookup the handler and run it, then continue to
		# recurse unless the handler returns False.

		try:
			fn = getattr(self, 'traverse_%s_%s_%s' % (step, ns, tag))
		except AttributeError:
			try:
				fn = getattr(self, 'traverse_%s_%s' % (step, ns))
			except AttributeError:
				try:
					fn = getattr(self, 'traverse_%s' % step)
				except AttributeError:
					fn = None

		if fn:
			steps = self.getAttr(node, 'stack:visited').split()
			steps.append(step)
			node.setAttribute('stack:visited', ' '.join(steps))
		else:
			steps = self.getAttr(node, 'stack:skipped').split()
			steps.append(step)
			node.setAttribute('stack:skipped', ' '.join(steps))
			
		if fn and not fn(node):
			return

		for child in node.childNodes:
			self._traverse(step, child)


	def collect(self, node):
		l = []
		for child in node.childNodes:
			if child.nodeType in [ child.TEXT_NODE, child.CDATA_SECTION_NODE]:
				l.append(child.nodeValue)
			elif child.nodeType == child.ELEMENT_NODE:
				try:
					fn = eval('self.collect_%s_%s' % (child.prefix, 
									  child.localName))
				except AttributeError:
					fn = None
				if fn:
					l.append(fn(child))
		return ''.join(l)



	## ---------------------------------------------------- ##
	## Traverse						##
	## ---------------------------------------------------- ##

	##
	## setup
	##

	# <stack:profile>
	
	def traverse_setup_stack_profile(self, node):
		if node.attributes:
			attrs = node.attributes.getNamedItem('stack:attrs')
			if attrs:
				dict = eval(attrs.value)
				for (k,v) in dict.items():
					self.attrs[k] = v
		else:
			self.debug('error - <stack:profile> missing stack:attrs', node)
		return True

	# <*>

	def traverse_setup(self, node):

		# Store the order of traversal of the nodes

		nodefile = self.getAttr(node, 'stack:file')

		if nodefile and nodefile not in self.nodeFilesDict:
			self.nodeFilesDict[nodefile] = True
			self.nodeFilesSection.append(nodefile)

		return True
		

		


	##
	## prune
	##

	# <*>

	def traverse_prune(self, node):
		arch	= self.getAttr(node, 'stack:arch', consume=True)
		osname	= self.getAttr(node, 'stack:os', consume=True)
		release = self.getAttr(node, 'stack:release', consume=True)
		cond	= self.getAttr(node, 'stack:cond', consume=True)
		expr    = stack.cond.CreateCondExpr(arch, osname, release, cond)

		if not expr: # no cond keep going
			return True

		passed = stack.cond.EvalCondExpr(expr, self.attrs)
		self.debug('info - cond is %s: %s' % (passed, expr), node)
		if not passed:
			parent = node.parentNode
			if parent: # node might be orphaned
				parent.removeChild(node)
			return False # subtree is gone stop

		return True

	##
	## expand
	##
		
	# <stack:file>

	def traverse_expand_stack_file(self, node):
	
		fileName    = self.getAttr(node, 'stack:name')
		fileMode    = self.getAttr(node, 'stack:mode')
		fileOwner   = self.getAttr(node, 'stack:owner')
		filePerms   = self.getAttr(node, 'stack:perms')
		fileQuoting = self.getAttr(node, 'stack:vars')
		fileCommand = self.getAttr(node, 'stack:expr')
		fileRCS	    = self.getAttr(node, 'stack:rcs')
		fileText    = self.collect(node)

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

		node.parentNode.replaceChild(self.doc.createTextNode(s), node)
		return False

	##
	## main
	##

	# <stack:profile>

	def traverse_main_stack_profile(self, node):
		return True

	# <stack:package>

	def traverse_main_stack_package(self, node):
		nodefile = self.getAttr(node, 'stack:file')
		rpms	 = self.collect(node).strip().split()
		type	 = self.getAttr(node, 'stack:type')

		if self.getAttr(node, 'stack:disable'):
			enabled = False
		else:
			enabled = True

		for rpm in rpms:
			if type == 'meta':
				rpm = '@%s' % rpm
			self.packageSet.append(rpm, enabled, nodefile)
		return False

	# <stack:stacki>

	def traverse_main_stack_stacki(self, node):
		self.stackiSection.append(self.collect(node),
					  self.getAttr(node, 'stack:file'))
		node.parentNode.removeChild(node)
		return False

	# <stack:debug>
	
	def traverse_main_stack_debug(self, node):
		self.debugSection.append(self.collect(node), 
					 self.getAttr(node, 'stack:file'))
		node.parentNode.removeChild(node)
		return False

	# <*>

	def traverse_main(self, node):
		ns    = node.prefix
		tag   = node.localName

		attrs = []

		for (key, val) in node.attributes.items():
			if key == 'stack:file':
				continue
			attrs.append('%s="%s"' % (key, val))
		
		msg = 'error - <%s:%s' % (ns, tag)
		if attrs:
			msg += ' '
			msg += ' '.join(attrs)
		msg += '> no main handler'
		self.debug(msg, node)

		return True

	
	##
	## post
	##

	# <*>

	def traverse_post(self, node):

		# stack:gc="true" mean garabage collect
		# the node.
		#
		# Any previous traversal can set this attribute
		# to have the tag removed from the tree.


		gc = self.getAttr(node, 'stack:gc')
		gc = str2bool(gc)

		if gc:
			node.parentNode.removeChild(node)
		return True


	## ---------------------------------------------------- ##
	## Generate						##
	## ---------------------------------------------------- ##
			
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




