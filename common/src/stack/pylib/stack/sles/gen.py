#! /opt/stack/bin/python
# 
# @SI_Copyright@
# @SI_Copyright@

import string
import os
import tempfile
import xml.dom.minidom
from stack.bool import str2bool
import stack.gen


class ExpandingTraversor(stack.gen.Traversor):

	stages   = { 'install-pre'     : 'pre-scripts',
		     'install-pre-pkg' : 'postpartitioning-scripts',
		     'install-post'    : 'chroot-scripts',
		     'boot-pre'        : 'post-scripts',
		     'boot-post'       : 'init-scripts' }


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
		nodeid   = self.getAttr(node, 'stack:id')
		nodefile = self.getAttr(node, 'stack:file')
		stage    = self.getAttr(node, 'stack:stage',  default='install-post')
		chroot   = self.getAttr(node, 'stack:chroot', default='true')
		shell    = self.getAttr(node, 'stack:shell')

		if shell == 'python':
			shell = '/opt/stack/bin/python3'

		stagename = self.stages[stage]
		if not stagename == 'chroot-scripts':
			chroot = '' # setting only valid for chroot-scripts


		# <scripts>
		#   <STAGE config:type="list">
		#     <script>
		#       <filename>stacki-ipmi.sh</filename>
		#       <interpreter>SHELL</interpreter>
		#       <chrooted config:type="boolean">true|flase</chrooted>
		#       <source>
		#       ...
		#       </source>
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

		if chroot:
			chrooted = self.newElementNode('sles:chrooted')
			self.setAttribute(chrooted, 'config:type', 'boolean')
			chrooted.appendChild(self.newTextNode(shell))
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
			<packages config:type="list">
			<package>?</package>
			...
			</package>
		</software>

		"""

		packages = self.newElementNode('sles:packages')
		self.setAttribute(packages, 'config:type', 'list')

		for rpm in self.collect(node).strip().split():
			package = self.newElementNode('sles:package')
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
		self.outers  = { }
		self.scripts = [ ]

	def post(self):
		self.gen.scriptsSection.append('<scripts>')
		for child in self.scripts:
			self.gen.scriptsSection.append(child.toxml())
		self.gen.scriptsSection.append('</scripts>')

	def traverse_stack_profile(self, node):
		"""<stack:profile>

		Grab the namespace information out of the outermost
		tag and build the header for the final document.

		"""
		slesNS   = self.getAttr(self.gen.root, 'xmlns:sles')
		configNS = self.getAttr(self.gen.root, 'xmlns:config')
		xiNS     = self.getAttr(self.gen.root, 'xmlns:xi')

		section = self.gen.headerSection
		section.append('<?xml version="1.0"?>')
		section.append('<!DOCTYPE profile>')
		section.append('<profile xmlns="%s" xmlns:config="%s" xmlns:xi="%s">' % 
			       (slesNS, configNS, xiNS))

		section = self.gen.footerSection
		section.append('</profile>')
		return True


	def traverse_sles_package(self, node):
		"""<sles:package>

		"""
		nodefile = self.getAttr(node, 'stack:file')
		pkg	 = self.collect(node).strip()

		if node.parentNode.nodeName == 'sles:packages':
			enabled = True
		elif node.parentNode.nodeName == 'sles:remove-packages':
			enabled = False

		self.gen.packageSet.append(pkg, enabled, nodefile)
		self.traverse_sles(node)
		return False


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
		self.headerSection  = stack.gen.ProfileSection()
		self.footerSection  = stack.gen.ProfileSection()
		self.nativeSection  = stack.gen.ProfileSection()
		self.scriptsSection = stack.gen.ProfileSection()

		self.setOS('sles')
		self.setArch('x86_64')


	def traversors(self):
		return [ ExpandingTraversor(self), 
			 DefraggingTraversor(self), 
			 MainTraversor(self) ]

	def post(self):
		for child in self.root.childNodes:
			self.nativeSection.append(child.toxml())

	def generate_header(self):
		return self.headerSection.generate()

	def generate_native(self):
		return self.nativeSection.generate()

	def generate_scripts(self):
		return self.scriptsSection.generate()

	def generate_footer(self):
		return self.footerSection.generate()


	def generate_packages(self):
		dict	 = self.packageSet.getPackages()
		enabled	 = dict['enabled']
		disabled = dict['disabled']
		section	 = stack.gen.ProfileSection()

		s = ""
		for (nodefile, rpms) in enabled.items():
			if rpms:
				rpms.sort()
				s = s + ' %s' % ' '.join(rpms)
		if s:
			section.append("zypper install -f -y %s" %
				       s, None)

		return section.generate()


