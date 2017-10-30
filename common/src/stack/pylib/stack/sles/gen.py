#! /opt/stack/bin/python
# 
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.bool import str2bool
import stack.gen


class BashProfileTraversor(stack.gen.MainTraversor):

	def shellPackages(self, enabled, disabled):
		if enabled:
			return 'zypper install -f -y %s' % ' '.join(enabled)

		return None
		

class ExpandingTraversor(stack.gen.Traversor):

	stages	 = { 'install-pre'	   : 'pre-scripts',
		     'install-pre-package' : 'postpartitioning-scripts',
		     'install-post'	   : 'chroot-scripts',
		     'boot-pre'		   : 'post-scripts',
		     'boot-post'	   : 'init-scripts' }


	def pre(self):
		self.natives = [ ]

	def post(self):
		for child in self.natives:
			self.gen.root.appendChild(child)

	def traverse_stack_native(self, node):
		"""<stack:native lang="yast">

		Store the yast sections and delete everyone else.
		"""
		lang = self.getAttr(node, 'stack:lang')

		if lang == 'yast':
			for child in node.childNodes:
				self.natives.append(child.cloneNode(deep=True))

		node.parentNode.removeChild(node)
		return False


	def traverse_stack_script(self, node):
		nodeid	 = self.getAttr(node, 'stack:id')
		nodefile = self.getAttr(node, 'stack:file')
		stage	 = self.getAttr(node, 'stack:stage',  default='install-post')
		chroot	 = self.getAttr(node, 'stack:chroot', default='true')
		shell	 = self.getAttr(node, 'stack:shell', default='shell')

		stagename = self.stages[stage]
		if not stagename == 'chroot-scripts':
			chroot = '' # setting only valid for chroot-scripts


		# <scripts>
		#   <STAGE config:type="list">
		#     <script>
		#	<filename>stacki-ipmi.sh</filename>
		#	<interpreter>SHELL</interpreter>
		#	<chrooted config:type="boolean">true|flase</chrooted>
		#	<source>
		#	...
		#	</source>
		#     </script>
		#   </STAGE>
		# </scripts>


		root = self.newElementNode('sles:scripts')

		scripttype = self.newElementNode('sles:%s' % stagename)
		self.setAttribute(scripttype, 'config:type', 'list')
		root.appendChild(scripttype)

		script = self.newElementNode('sles:script')
		scripttype.appendChild(script)

		filename = self.newElementNode('sles:filename')
		filename.appendChild(self.newTextNode('%s-%s' % (stage, nodeid)))
		script.appendChild(filename)

		if shell:
			interpreter = self.newElementNode('sles:interpreter')
			interpreter.appendChild(self.newTextNode(shell))
			script.appendChild(interpreter)

		if stagename == 'chroot-scripts':
			chrooted = self.newElementNode('sles:chrooted')
			self.setAttribute(chrooted, 'config:type', 'boolean')
			chrooted.appendChild(self.newTextNode(chroot))
			script.appendChild(chrooted)

		source = self.newElementNode('sles:source')
		source.appendChild(self.newTextNode(self.collect(node)))
		script.appendChild(source)

		node.parentNode.replaceChild(root, node)
		return False




	def traverse_stack_package(self, node):
		"""Expands <stack:package> to native autoyast syntax, later passes
		will collect all these section to create a single
		<software> section.

		<software>
			<patterns config:type="list"> <!-- stack:type="meta" -->
				<pattern>?</pattern>
			</patterns>
			<packages config:type="list"> 
				<package>?</package>
				...
			</package>
		</software>

		"""

		meta	 = self.getAttr(node, 'stack:meta', default='false')
		meta     = str2bool(meta)

		enabled  = self.getAttr(node, 'stack:enable', default='true')
		enabled  = str2bool(enabled)


		if not meta:
			packages = self.newElementNode('sles:packages')
			self.setAttribute(packages, 'config:type', 'list')

			for rpm in self.collect(node).strip().split():
				package = self.newElementNode('sles:package')
				package.appendChild(self.newTextNode(rpm))
				packages.appendChild(package)
		else:
			packages = self.newElementNode('sles:patterns')
			self.setAttribute(packages, 'config:type', 'list')

			for rpm in self.collect(node).strip().split():
				package = self.newElementNode('sles:pattern')
				package.appendChild(self.newTextNode(rpm))
				packages.appendChild(package)

		software = self.newElementNode('sles:software')
		software.appendChild(packages)

		node.parentNode.replaceChild(software, node)
		return False


class DefraggingTraversor(stack.gen.Traversor):

	def pre(self):
		self.fragments = { }

	def traverse_sles(self, node):
		"""Finds all the config:type=list <sles:*> elements and moves them all
		into a single hierarchy.

		"""

		if not self.getAttr(node, 'config:type') == 'list':
			return True

		if node.nodeName not in self.fragments:

			# Find all the config:type=list tags and
			# remember the first one for each tag name

			self.fragments[node.nodeName] = node
		else:

			# For subsequent tags move all the children to
			# the master (above). Also check if any other
			# siblings are at the same level, if not mark
			# the parent node for later deletion (can't
			# safely remove the parent right now)

			master = self.fragments[node.nodeName]
			for child in node.childNodes:
				master.appendChild(child.cloneNode(deep=True))


			parent = node.parentNode
			remove = True

			node.parentNode.removeChild(node)
			for child in parent.childNodes:
				if child.nodeType == child.ELEMENT_NODE:
					remove = False
					break

			if remove:
				parent.setAttribute('stack:gc', 'true')


		return False 




class MainTraversor(stack.gen.MainTraversor):

	def pre(self):
		self.scripts  = [ ]
		self.software = [ ]

	def post(self):
		self.gen.softwareSection.append('<software>')
		for child in self.software:
			self.gen.softwareSection.append(child.toxml())
		self.gen.softwareSection.append('</software>')

		self.gen.scriptsSection.append('<scripts>')
		for child in self.scripts:
			self.gen.scriptsSection.append(child.toxml())
		self.gen.scriptsSection.append('</scripts>')

	def traverse_stack_profile(self, node):
		"""<stack:profile>

		Grab the namespace information out of the outermost
		tag and build the header for the final document.

		"""
		slesNS	 = self.getAttr(self.gen.root, 'xmlns:sles')
		configNS = self.getAttr(self.gen.root, 'xmlns:config')
		xiNS	 = self.getAttr(self.gen.root, 'xmlns:xi')
		stackNS	 = self.getAttr(self.gen.root, 'xmlns:stack')

		section = self.gen.headerSection
		section.append('<?xml version="1.0"?>')
		section.append('<!DOCTYPE profile>')
		section.append('<profile xmlns="%s" xmlns:config="%s" xmlns:xi="%s" xmlns:stack="%s">' % 
			       (slesNS, configNS, xiNS, stackNS))

		section = self.gen.footerSection
		section.append('</profile>')
		return True


	def traverse_sles_package(self, node):
		"""<sles:package>

		"""
		nodefile = self.getAttr(node, 'stack:file')
		pkg	 = self.collect(node).strip()

		if node.parentNode.nodeName == 'sles:packages':
			self.gen.packageSet.append(pkg, True, nodefile)
		elif node.parentNode.nodeName == 'sles:remove-packages':
			self.gen.packageSet.append(pkg, False, nodefile)

		self.traverse_sles(node)
		return False


	def traverse_sles_software(self, node):
		"""Handle multiple <sles:software> sections by recording them in a
		ProfileSection and marking the XML element for
		garbarge collection.

		"""
		for child in node.childNodes:
			self.software.append(child)
		node.setAttribute('stack:gc', 'true')
		return True # keep going


	def traverse_sles_scripts(self, node):
		"""Handle multiple <sles:scripts> sections by recording them in a
		ProfileSection and marking the XML element for
		garbarge collection.

		"""
		for child in node.childNodes:
			self.scripts.append(child)
		node.setAttribute('stack:gc', 'true')
		return True # keep going


	def traverse_sles(self, node):
		"""<sles:*>

		"""
		node.tagName = node.localName
		self.getAttr(node, 'stack:file', consume=True)
		return True


	def traverse_xi(self, node):
		"""<xi:*>

		"""
		self.getAttr(node, 'stack:file', consume=True)
		return True



class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)
		self.headerSection   = stack.gen.ProfileSection()
		self.nativeSection   = stack.gen.ProfileSection()
		self.footerSection   = stack.gen.ProfileSection()
		self.softwareSection = stack.gen.ProfileSection()
		self.scriptsSection  = stack.gen.ProfileSection()

		self.setOS('sles')
		self.setArch('x86_64')


	def traversors(self):
		profileType = self.getProfileType()
		workers	    = [ ]

		if profileType == 'native':
			workers.extend([ ExpandingTraversor(self), 
					 DefraggingTraversor(self), 
					 MainTraversor(self) ])
		elif profileType == 'bash':
			workers.extend([ BashProfileTraversor(self) ])

		return workers

	def post(self):
		"""Add the final XML document to the nativeSection.

		"""
		for child in self.root.childNodes:
			self.nativeSection.append(child.toxml())

	def generate_native(self):
		profile = self.headerSection.generate()
		profile.extend(self.nativeSection.generate())
		profile.extend(self.softwareSection.generate())
		profile.extend(self.scriptsSection.generate())
		profile.extend(self.footerSection.generate())
		return profile

	def generate_bash(self):
		profile	 = [ '#! /bin/bash' ]
		profile.extend(self.shellSection.generate())
		return profile


