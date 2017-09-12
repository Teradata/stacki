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

import stack.gen	


class BashProfileTraversor(stack.gen.MainTraversor):

	def shellPackages(self, enabled, disabled):
		return 'yum install -f -y %s' % ' '.join(enabled)
		
		
class LegacyTraversor(stack.gen.Traversor):
	"""Convert kickstart-xml into Stacki Universal XML."""
	
	def legacy2script(self, node, stage):
		nodefile = self.getAttr(node, 'stack:file')
		nodeid   = self.getAttr(node, 'stack:id')
		shell    = self.getAttr(node, 'stack:shell')
		chroot   = self.getAttr(node, 'stack:chroot')

		attrs = []
		for (key, val) in node.attributes.items():
			if key == 'stack:file': # omit from msg
				continue
			attrs.append('%s="%s"' % (key, val))
		msg = '<%s' % node.tagName
		if attrs:
			msg += ' '
			msg += ' '.join(attrs)
		msg += '> legacy syntax'
		self.debug(msg, level="warn")

		new = self.newElementNode('stack:script')
		self.setAttribute(new, 'stack:file',  nodefile)
		self.setAttribute(new, 'stack:stage', stage)
		self.setAttribute(new, 'stack:id',    'legacy-%s' % nodeid)
		if shell:
			self.setAttribute(new, 'stack:shell', shell)
		if chroot:
			self.setAttribute(new, 'stack:chroot', chroot)

		for child in node.childNodes:
			new.appendChild(child.cloneNode(deep=True))

		node.parentNode.replaceChild(new, node)


	def traverse_stack_pre(self, node):
		"""<stack:pre>

		Rewrite to <stack:script stack:stage="install-pre">

		"""
		self.legacy2script(node, 'install-pre')
		return False

	def traverse_stack_post(self, node):
		"""<stack:post>

		Rewrite to <stack:script stack:stage="install-post">

		"""
		self.legacy2script(node, 'install-post')
		return False

	def traverse_stack_boot(self, node):
		"""<stack:boot>

		Rewrite to <stack:script stack:stage="boot-[pre|post]">

		"""
		order = self.getAttr(node, 'stack:order', default='pre')
		self.legacy2script(node, 'boot-%s' % order)
		return False


class MainTraversor(stack.gen.MainTraversor):

	stages   = { 'install-pre'         : 'pre',
		     'install-pre-package' : 'pre-install',
		     'install-post'        : 'post' }

	def traverse_stack_native(self, node):
		lang = self.getAttr(node, 'stack:lang')

		if lang == 'kickstart':
			self.gen.nativeSection.append(self.collect(node),
						      self.getAttr(node, 'stack:file'))
		return False


	def traverse_stack_script(self, node):
		"""<stack:script>

		"""
		nodefile = self.getAttr(node, 'stack:file')
		stage    = self.getAttr(node, 'stack:stage',  default='install-post')
		shell    = self.getAttr(node, 'stack:shell')
		flags    = [ ]

		if stage == 'install-post':
			chroot = self.getAttr(node, 'stack:chroot', default='true')
		else:
			chroot = ''

		if not chroot == 'true':
			flags.append('--nochroot')
			flags.append('--log /mnt/sysimage%s' % self.gen.log)
		else:
			flags.append('--log %s' % self.gen.log)

		if shell:
			flags.append('--interpreter %s' % shell)

		script = [ ]
		if stage in self.stages:
			script.append('%%%s %s' % (self.stages[stage], 
						   ' '.join(flags)))
			script.append(self.collect(node))
			script.append('%end')
		elif stage in [ 'boot-pre', 'boot-post' ]:
			boot, when = stage.split('-')

			script = [ '%%post --log %s' % self.gen.log ]
			script.append("cat >> /etc/sysconfig/stack-%s << '__EOF__'" % when)
			script.append(self.collect(node))
			script.append('__EOF__')
			script.append('%end')

		self.gen.scriptSection.append('\n'.join(script), nodefile)
		return False


class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)
		self.nativeSection	 = stack.gen.ProfileSection()
		self.scriptSection	 = stack.gen.ProfileSection()

		# We could set these elsewhere but this is the current
		# definition of the RedHat Generator.
		#
		# We used to do i386 (not anymore)

		self.setOS('redhat')
		self.setArch('x86_64')

	def traversors(self):
		profileType = self.getProfileType()
		workers     = [ LegacyTraversor(self) ]

		if profileType == 'native':
			workers.extend([ MainTraversor(self) ])
		elif profileType == 'bash':
			workers.extend([ BashProfileTraversor(self) ])

		return workers

	def generate_native(self):

		doc = self.nativeSection.generate() # <stack:native>

		packages = self.packageSet.getPackages()
		section	 = stack.gen.ProfileSection()
		section.append('%packages --ignoremissing')
		for (nodefile, pkgs) in packages['enabled'].items():
			for pkg in sorted(pkgs):
				section.append(pkg, nodefile)

		for (nodefile, pkgs) in packages['disabled'].items():
			for pkg in sorted(pkgs):
				section.append('-%s' % pkg, nodefile)
		section.append('%end')
		doc.extend(section.generate()) # <stack:package>

		doc.extend(self.scriptSection.generate())

		return doc



