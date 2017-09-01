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
import stack.gen	
		
class MainTraversor(stack.gen.MainTraversor):

	def traverse_stack_native(self, node):
		lang = self.getAttr(node, 'stack:lang')

		if lang == 'kickstart':
			self.gen.nativeSection.append(self.collect(node),
						      self.getAttr(node, 'stack:file'))
			return False
		return True


	def traverse_stack_pre(self, node):
		"""<stack:pre>

		"""
		nodefile = self.getAttr(node, 'stack:file')
		shell    = self.getAttr(node, 'stack:shell')
		flags    = [ ]

		flags.append('--log=%s' % self.gen.log)
		if shell:
			flags.append('--interpreter %s' % shell)

		script = '%%pre %s\n%s\n%%end' % (' '.join(flags),
						  self.collect(node))
			
		self.gen.preSection.append(script, nodefile)
		return False


	def traverse_stack_post(self, node):
		"""<stack:post>

		"""
		nodefile = self.getAttr(node, 'stack:file')
		chroot   = self.getAttr(node, 'stack:chroot', default=True)
		shell    = self.getAttr(node, 'stack:shell')
		flags    = [ ]

		if not chroot:
			flags.append('--nochroot')
			flags.append('--log=/mnt/sysimage%s' % self.gen.log)
		else:
			flags.append('--log=%s' % self.gen.log)

		if shell:
			if shell == 'python':
				shell = '/opt/stack/bin/python3'
			flags.append('--interpreter %s' % shell)

		if self.gen.getProfileType() == 'native':
			script = '%%post %s\n%s\n%%end' % (' '.join(flags), 
							   self.collect(node))

		elif self.gen.getProfileType() == 'shell' and chroot:
			if shell:
				script = self.bashify(shell, self.collect(node))
			else:
				script = self.collect(node)
			
		self.gen.postSection.append(script, nodefile)
		return False
		
	def traverse_stack_boot(self, node):
		"""<stack:boot>
		
		"""
		nodefile = self.getAttr(node, 'stack:file')
		order	 = self.getAttr(node, 'stack:order')
		
		if not order:
			order = 'pre'
		
		s = ''

		if self.gen.getProfileType() == 'native':
			s = '%%post --log=%s\n' % self.gen.log

		s += "cat >> /etc/sysconfig/stack-%s << '__EOF__'\n" % order
		s += '%s' % self.collect(node)
		s += '__EOF__\n'

		if self.gen.getProfileType() == 'native':
			s += '\n%end'

		self.gen.bootSection[order].append(s, nodefile)
		return False


class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)
		self.nativeSection	 = stack.gen.ProfileSection()
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

	def traversors(self):
		"""Returns a list of Traversor that derived classes can change.

		"""
		return [ MainTraversor(self) ]

	def generate_native(self):
		return self.nativeSection.generate()

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
		result = []

		for line in self.bootSection['pre'].generate():
			result.append(line)
		for line in self.bootSection['post'].generate():
			result.append(line)

		return result


