#! @PYTHON@
#
# $Id$
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
#
# $Log$
# Revision 1.19  2010/09/07 23:53:07  bruno
# star power for gb
#
# Revision 1.18  2009/05/01 19:07:07  mjk
# chimi con queso
#
# Revision 1.17  2009/04/27 18:03:33  bruno
# remove dead setRCS* and getRCS* functions
#
# Revision 1.16  2009/01/08 01:20:58  bruno
# for anoop
#
# Revision 1.15  2008/10/18 00:56:01  mjk
# copyright 5.1
#
# Revision 1.14  2008/08/20 23:41:22  bruno
# 'lan' is no longer part of the distro path
#
# Revision 1.13  2008/03/06 23:41:43  mjk
# copyright storm on
#
# Revision 1.12  2008/01/04 21:40:53  bruno
# closer to V
#
# Revision 1.11  2007/06/23 04:03:23  mjk
# mars hill copyright
#
# Revision 1.10  2006/09/11 22:47:16  mjk
# monkey face copyright
#
# Revision 1.9  2006/08/10 00:09:37  mjk
# 4.2 copyright
#
# Revision 1.8  2006/01/16 06:48:58  mjk
# fix python path for source built foundation python
#
# Revision 1.7  2005/10/12 18:08:39  mjk
# final copyright for 4.1
#
# Revision 1.6  2005/09/16 01:02:19  mjk
# updated copyright
#
# Revision 1.5  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.4  2005/06/01 20:33:00  mjk
# fixed for lastest pylib, still a bad idea
#
# Revision 1.3  2005/05/24 21:21:54  mjk
# update copyright, release is not any closer
#
# Revision 1.2  2005/04/06 17:54:13  mjk
# fix extra newlines (bug reported by platform
#
# Revision 1.1  2005/03/01 02:02:48  mjk
# moved from core to base
#
# Revision 1.4  2005/02/11 23:38:16  mjk
# - blow up the bridge
# - kgen and kroll do actually work (but kroll is not complete)
# - file,roll attrs added to all tags by kpp
# - gen has generator,nodefilter base classes
# - replaced rcs ci/co code with new stuff
# - very close to adding rolls on the fly
#
# Revision 1.3  2005/02/02 00:58:08  mjk
# DOM
#
# Revision 1.2  2005/02/02 00:16:56  mjk
# *** empty log message ***
#
# Revision 1.1  2005/02/01 01:49:21  mjk
# KRoll
#

import os
import sys
import string
import socket
import syslog
import stack.kickstart
import stack.gen
import re
import time
from xml.dom			import ext
from xml.dom.ext.reader		import Sax2
from xml.sax._exceptions	import SAXParseException

class NodeFilter(stack.gen.NodeFilter):

	def __init__(self, arch, rolls):
		self.os = os.uname()[0].lower()
		stack.gen.NodeFilter.__init__(self, arch, self.os)
		self.rolls = rolls
		
	def isFromRolls(self, node):
		try:
			roll = node.attributes.getNamedItem((None, 'roll'))
			if roll.value in self.rolls:
				return 1
		except AttributeError:
			pass
		return 0
		
	def acceptNode(self, node):
		if node.nodeName == 'kickstart':
			return self.FILTER_ACCEPT
			
		if not self.isCorrectCond(node):
			return self.FILTER_SKIP

		if not self.isFromRolls(node):
			return self.FILTER_SKIP

		tags = [ 'description', 'package', 'post' ]
		if node.nodeName not in tags:
			return self.FILTER_SKIP			

		return self.FILTER_ACCEPT


class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)
		self.ks			= {}
		self.ks['order']	= []
		self.ks['rpms']		= []
		self.ks['post']		= []
		self.rolls		= []
		self.rpms		= None
		
	def setRolls(self, rolls):
		self.rolls = rolls
		
	def getRolls(self):
		return self.rolls
		
	def setRPMS(self, rpms):
		self.rpms = rpms
		
	def getRPMS(self):
		return self.rpms
		
	##
	## Parsing Section
	##
	
	def parse(self, doc):
		filter = NodeFilter(self.getArch(), self.getRolls())
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()
		while node:
			if node.nodeName != 'kickstart':
				eval('self.handle_%s(node)' % node.nodeName)
			node = iter.nextNode()
			
	# <description>
				
	def handle_description(self, node):
		attr = node.attributes
		file = attr.getNamedItem((None, 'file'))
		self.ks['order'].append(file.value)
		
	# <package>
		
	def handle_package(self, node):

		# ignore disabled packages
		
		if self.isDisabled(node):
			return
			
		# we don't support meta packages, so ignore them
		
		if self.isMeta(node):
			return
		
		basename = string.strip(self.getChildText(node))
		for rpm in self.rpms:
			if rpm.getBaseName() == basename:
				self.ks['rpms'].append(rpm.getFullName())

	# <post>
	
	def handle_post(self, node):
		attr = node.attributes
		if attr.getNamedItem((None, 'arg')):
			arg = attr.getNamedItem((None, 'arg')).value
		else:
			arg = ''
		list = []
		list.append(arg)
		list.append(self.getChildText(node))
		self.ks['post'].append(list)
		
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
			
	def generate(self, section):
		"""Dump the requested section of the kickstart file.  If none 
		exists do nothing."""
		try:
			f = getattr(self, "generate_%s" % section)
			f()
		except:
			pass
		
	def generate_order(self):
		print '#'
		print '# Node Traversal Order'
		print '#'
		for line in self.ks['order']:
			print '#', line
		print '#'
		print

	def generate_packages(self):
		print '#'
		print '# Kickstart Packages Section'
		print '#'
		for rpm in self.ks['rpms']:
			print 'rpm -Uvh --force --nodeps ', rpm
		print

	def generate_post(self):
		print '#'
		print '# Kickstart Post Section'
		print '#'
		for list in self.ks['post']:
			print '#', list[0]
			print string.join(list[1:], '\n')
		print
			


class App(stack.kickstart.Application):

	def __init__(self, argv):
		stack.kickstart.Application.__init__(self, argv)
		self.usage_name		= 'Kickstart Roll'
		self.usage_version	= '@VERSION@'
		self.generator		= Generator()

	def run(self):
		rolls = self.args
		if not rolls:
			self.usage()
			sys.exit(-1)

		self.connect()
		
		try:
			hostname = string.split(socket.gethostname(), '.')[0]
			hostaddr = socket.gethostbyname(hostname)
		except:
			print 'error - cannot determine hostname'
			sys.exit(-1)

		try:
			self.execute('select '
				'appliances.graph, '
				'appliances.node, '
				'distributions.name '
				'from nodes, memberships, appliances, '
				'distributions where nodes.name="%s" and '
				'nodes.membership=memberships.id and '
				'memberships.appliance=appliances.id and '
				'memberships.distribution=distributions.id'
				% hostname)
			graph, node, dist = self.fetchone()
		except:
			print 'error = cannot find host in database'
			sys.exit(-1)
		
		self.dist.setDist(os.path.join(dist))
		self.dist.setArch(self.arch)
		self.dist.build()
		distroot = self.dist.getReleasePath()
		buildroot = os.path.join(distroot, 'build')

		kpp = 'kpp --graph=%s --client=%s --client-ip=%s ' \
			'--arch=%s --distribution=%s %s' % (
			graph, hostname, hostaddr, self.arch, 
			self.dist.getReleasePath(), node)

		try:
			os.chdir(buildroot)
		except:
			print 'error - cannot find distribution (%s)' % \
				buildroot
			sys.exit(-1)

		text = []
		for line in os.popen(kpp).readlines():
			text.append(line[:-1])
		reader = Sax2.Reader()
		doc = reader.fromString(string.join(text, '\n'))
				
		self.generator.setArch(self.arch)
		self.generator.setRolls(rolls)
		self.generator.setRPMS(self.dist.getRPMS())
		self.generator.parse(doc)

		print '#!/bin/sh'		
		print '#'
		print '# %s version %s' % (self.usage_name, self.usage_version)
		print '#'

		for s in [ 'order', 'packages', 'post' ]:
			self.generator.generate(s)



app = App(sys.argv)
app.parseArgs()
app.run()

