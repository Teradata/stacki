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

class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)	

		self.fragments = { }
		self.scripts   = [ ]

		self.setOS('sles')
		self.setArch('x86_64')


	def parse(self, xml_string):
		stack.gen.Generator.parse(self, xml_string)


	## ---------------------------------------------------- ##
	## Traverse						##
	## ---------------------------------------------------- ##

	##
	## expand
	##

	# <stack:package>

	def traverse_expand_stack_package(self, node):
		slesNS   = self.getAttr(self.root, 'xmlns:sles')
		configNS = self.getAttr(self.root, 'xmlns:config')

		# <software>
		#	<packages config:type="list">
		#		<package>?</package>
		#		...
		#	</package>
		# </software>

		packages = self.doc.createElementNS(slesNS, 'sles:packages')
		packages.setAttributeNS(configNS, 'config:type', 'list')

		for rpm in self.collect(node).strip().split():
			package = self.doc.createElementNS(slesNS, 'sles:package')
			package.appendChild(self.doc.createTextNode(rpm))
			packages.appendChild(package)

		software = self.doc.createElementNS(slesNS, 'sles:software')
		software.appendChild(packages)

		node.parentNode.replaceChild(software, node)

		return False

	##
	## pre
	##

	# <sles:*>

	def traverse_pre_sles(self, node):


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

		

	##
	## main
	##

	# <stack:post>

	def traverse_main_stack_post(self, node):
		# For now nuke any post sections, but this should really
		# be part of SUX
		node.parentNode.removeChild(node)
		return False

	# <sles:package>

	def traverse_main_sles_package(self, node):
		nodefile = self.getAttr(node, 'stack:file')
		pkg	 = self.collect(node).strip()

		if node.parentNode.nodeName == 'sles:packages':
			enabled = True
		elif node.parentNode.nodeName == 'sles:remove-packages':
			enabled = False

		self.packageSet.append(pkg, enabled, nodefile)
		self.traverse_main_sles(node)
		return False


	# <sles:scripts>

	def traverse_main_sles_scripts(self, node):
		for child in node.childNodes:
			self.scripts.append(child)
		node.setAttribute('stack:gc', 'true')
		return True # keep going


	# <sles:*>

	def traverse_main_sles(self, node):
		node.tagName = node.localName
		self.getAttr(node, 'stack:file', consume=True)
		return True


	# <xi:*>

	def traverse_main_xi(self, node):
		self.getAttr(node, 'stack:file', consume=True)
		return True



	## ---------------------------------------------------- ##
	## Generate						##
	## ---------------------------------------------------- ##

	def generate_native(self):
		section = stack.gen.ProfileSection()

		slesNS   = self.getAttr(self.root, 'xmlns:sles')
		configNS = self.getAttr(self.root, 'xmlns:config')
		xiNS     = self.getAttr(self.root, 'xmlns:xi')

		section.append('<?xml version="1.0"?>')
		section.append('<!DOCTYPE profile>')
		section.append('<profile xmlns="%s" xmlns:config="%s" xmlns:xi="%s">' % (slesNS, configNS, xiNS))

		for child in self.root.childNodes:
			section.append(child.toxml())

		section.append('<scripts>')
		for child in self.scripts:
			section.append(child.toxml())
		section.append('</scripts>')

		section.append('</profile>')

		return section.generate()

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


