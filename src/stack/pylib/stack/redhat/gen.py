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
import os
import tempfile
import stack.gen	
		

class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)
		self.mainSection	 = ProfileSection()
		self.preSection		 = stack.gen.ProfileSection()
		self.postSection	 = stack.gen.ProfileSection()
		self.bootSection	 = {}
		self.bootSection['pre']	 = stack.gen.ProfileSection()
		self.bootSection['post'] = stack.gen.ProfileSection()
		self.shellSection	 = stack.gen.ProfileSection()

		# We could set these elsewhere but this is the current
		# definition of the RedHat Generator.
		#
		# We used to do i386 (not anymore)

		self.setOS('redhat')
		self.setArch('x86_64')

	## ---------------------------------------------------- ##
	## Traverse						##
	## ---------------------------------------------------- ##

	##
	## main
	##

	# <stack:main>

	def traverse_main_stack_main(self, node):
		nodefile = self.getAttr(node, 'stack:file')

		for child in node.childNodes:
			if child.nodeType in [ child.TEXT_NODE, child.CDATA_SECTION_NODE]:
				self.mainSection.append(child.nodeValue.strip(), nodefile)
		return False

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

	# <stack:pre>
	
	def traverse_main_stack_pre(self, node):
		nodefile	= self.getAttr(node, 'stack:file')
		interpreter	= self.getAttr(node, 'stack:interpreter')
		arg		= self.getAttr(node, 'stack:arg')

		s = '%pre'
		if interpreter:
			s += ' --interpreter %s' % interpreter
		s += ' --log=%s %s' % (self.log, arg)
		s += '\n%s' % self.collect(node)
		s += '\n%end'
			
		self.preSection.append(s, nodefile)
		return False


	# <stack:post>
	
	def traverse_main_stack_post(self, node):
		nodefile	= self.getAttr(node, 'stack:file')
		interpreter	= self.getAttr(node, 'stack:interpreter')
		arg		= self.getAttr(node, 'stack:arg')

		if self.getProfileType() == 'native':
			script = '%post'
			if interpreter:
				script += ' --interpreter %s' % interpreter
			if arg and '--nochroot' in arg:
				script += ' --log=/mnt/sysimage%s %s' % (self.log, arg)
			else:
				script += ' --log=%s %s' % (self.log, arg)
			script += '\n%s' % self.collect(node)
			script += '\n%end'

		elif self.getProfileType() == 'shell':

			section = self.collect(node)
			tmp	= tempfile.mktemp()

			if interpreter:
				script	= 'cat > %s << "__EOF_%s__"\n' % (tmp, tmp)
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
		return False
		
	# <stack:boot>
	
	def traverse_main_stack_boot(self, node):
		nodefile	= self.getAttr(node, 'stack:file')
		order		= self.getAttr(node, 'stack:order')
		
		if not order:
			order = 'pre'
		
		s = ''

		if self.getProfileType() == 'native':
			s = '%%post --log=%s\n' % self.log

		s += "cat >> /etc/sysconfig/stack-%s << '__EOF__'\n" % order
		s += '%s' % self.collect(node)
		s += '__EOF__\n'

		if self.getProfileType() == 'native':
			s += '\n%end'

		self.bootSection[order].append(s, nodefile)
		return False


	## ---------------------------------------------------- ##
	## Generate						##
	## ---------------------------------------------------- ##

	def generate_main(self):
		return self.mainSection.generate()

	def generate_packages(self):
		dict	 = self.packageSet.getPackages()
		enabled	 = dict['enabled']
		disabled = dict['disabled']
		section	 = stack.gen.ProfileSection()

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
			s = ""
			for (nodefile, rpms) in enabled.items():
				if rpms:
					rpms.sort()
					s = s + ' %s' % ' '.join(rpms)
			if s:
				section.append("yum install -y %s" % s, None)

		return section.generate()


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
			s += '\n%end'
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


