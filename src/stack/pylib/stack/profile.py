#! /opt/stack/bin/python
#
# @SI_Copyright@
#                               stacki.com
#                                  v3.3
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

from __future__ import print_function
import os
import sys
import string
import xml
import popen2
import socket
import base64
import syslog
import stack.sql
import stack.util
import stack.graph
import stack.cond
from xml.sax import saxutils
from xml.sax import handler
from xml.sax import make_parser

class RollHandler(handler.ContentHandler,
		  handler.DTDHandler,
		  handler.EntityResolver,
		  handler.ErrorHandler):

	def __init__(self):
		handler.ContentHandler.__init__(self)
		self.rollName  = ''
		self.edgeColor = None
		self.nodeColor = None
		self.nodeShape = 'ellipse'

	def getRollName(self):
		return self.rollName
	
	def getEdgeColor(self):
		return self.edgeColor

	def getNodeColor(self):
		return self.nodeColor

	def getNodeShape(self):
		return self.nodeShape
	
	# <roll>
	
	def startElement_roll(self, name, attrs):
		self.rollName = attrs.get('name')
		
	
	# <color>
	
	def startElement_color(self, name, attrs):
		if attrs.get('edge'):
			self.edgeColor = attrs.get('edge')
		if attrs.get('node'):
			self.nodeColor = attrs.get('node')


	def startElement(self, name, attrs):
		try:
			eval('self.startElement_%s(name, attrs)' % name)
		except AttributeError:
			pass

	def endElement(self, name):
		try:
			eval('self.endElement_%s(name)' % name)
		except AttributeError:
			pass


class AttributeHandler:

	def setAttributes(self, attrs):
		list = []
		list.append('<?xml version="1.0" standalone="no"?>\n')
		list.append('<!DOCTYPE stack-graph [\n')
		keys = attrs.keys()
		keys.sort()
		for k in keys:
			v = attrs[k]
			list.append('\t<!ENTITY %s "%s">\n' % (k, v))
		list.append(']>\n')
		self.header = string.join(list, '')

	def getXMLHeader(self):
		return self.header

	
class GraphHandler(handler.ContentHandler,
		   handler.DTDHandler,
		   handler.EntityResolver,
		   handler.ErrorHandler,
		   AttributeHandler):

        # TODO -- nuke the entities, this is dead code and confusing

	def __init__(self, attrs, entities={}, prune=True, directories=[ '.' ]):
		handler.ContentHandler.__init__(self)
		self.setAttributes(attrs)
		self.graph			= stack.util.Struct()
		self.graph.main			= stack.graph.Graph()
		self.graph.order		= stack.graph.Graph()
		self.attrs			= stack.util.Struct()
		self.attrs.main			= stack.util.Struct()
		self.attrs.main.default		= stack.util.Struct()
		self.attrs.order		= stack.util.Struct()
		self.attrs.order.default	= stack.util.Struct()
		self.attributes			= attrs
		self.entities			= entities # not used ?
		self.roll			= ''
		self.text			= ''
		self.os				= attrs['os']
		self.directories		= directories

		# Should we prune the graph while adding edges or not.
		# Prune is the answer for most cases while traversing
		# the graph. "Do Not Prune" is the answer when pictorial
		# representation of graph is required. 
		self.prune			= prune

	def getMainGraph(self):
		return self.graph.main

	def getOrderGraph(self):
		return self.graph.order

	def parseNode(self, node, eval=True, rcl=None):
		if node.name in [ 'HEAD', 'TAIL' ]:
			return
		
		nodesPath = []
		for dir in self.directories:
			nodesPath.append(os.path.join(dir, 'nodes'))

		# Find the xml file for each node in the graph.  If we
		# can't find one just complain and abort.

		xml = [ None, None, None ] # default, extend, replace
		for dir in nodesPath:
			if not xml[0]:
				file = os.path.join(dir, '%s.xml' % node.name)
				if os.path.isfile(file):
					xml[0] = file
			if not xml[1]:
				file = os.path.join(dir, 'extend-%s.xml'\
						    % node.name)
				if os.path.isfile(file):
					xml[1] = file
			if not xml[2]:
				file = os.path.join(dir, 'replace-%s.xml'\
						    % node.name)
				if os.path.isfile(file):
					xml[2] = file

		if not (xml[0] or xml[2]):
			raise stack.util.KickstartNodeError, \
			      'cannot find node "%s"' % node.name

		xmlFiles = [ xml[0] ]
		if xml[1]:
			xmlFiles.append(xml[1])
		if xml[2]:
			xmlFiles = [ xml[2] ]

		for xmlFile in xmlFiles:
		
			# 1st Pass
			#	- Expand XML Entities
			#	- Expand VAR tags (going away)
			#	- Expand EVAL tags
			#	- Expand INCLUDE/SINCLUDE tag
			#	- Logging for post sections

			fin = open(xmlFile, 'r')
			parser = make_parser()

			handler = Pass1NodeHandler(node, xmlFile, 
				self.entities, self.attributes, eval, rcl)
			parser.setContentHandler(handler)
			parser.feed(handler.getXMLHeader())

			linenumber = 0
			for line in fin.readlines():
				linenumber += 1
			
				# Some of the node files might have the <?xml
				# document header.  Since we are replacing
				# the XML header with our own (which includes
				# the entities) we need to skip it.
				
				if line.find('<?xml') != -1:
					continue
					
				# Send the XML to stderr for debugging before
				# we parse it.
				
				if os.environ.has_key('STACKDEBUG'):
					sys.stderr.write('[parse1]%s' % line)

				try:
					parser.feed(line)
				except:
					print('XML parse error in ' + \
						'file %s ' % xmlFile + \
						'on line %d\n' % linenumber)
					raise
				
			fin.close()
			
			# 2nd Pass
			#	- Annotate all tags with ROLL attribute
			#	- Annotate all tags with FILE attribute
			#	- Strip off KICKSTART tags
			#
			# The second pass is required since EVAL tags can
			# create their own XML, instead of requiring the
			# user to annotate we do it for them.
			
			parser = make_parser()
			xml = handler.getXML()
			handler = Pass2NodeHandler(node, self.attributes)
			parser.setContentHandler(handler)
			if os.environ.has_key('STACKDEBUG'):
				sys.stderr.write('[parse2]%s' % xml)
			parser.feed(xml)

			# Attach the final XML to the node object so we can
			# find it again.
			
			node.addXML(handler.getXML())
			node.addKSText(handler.getKSText())


	def addOrder(self):
		if self.graph.order.hasNode(self.attrs.order.head):
			head = self.graph.order.getNode(self.attrs.order.head)
		else:
			head = Node(self.attrs.order.head)

		if self.graph.order.hasNode(self.attrs.order.tail):
			tail = self.graph.order.getNode(self.attrs.order.tail)
		else:
			tail = Node(self.attrs.order.tail)

		e = OrderEdge(head, tail, self.attrs.order.gen)
		e.setRoll(self.roll)
		self.graph.order.addEdge(e)


	def addEdge(self):
		if self.graph.main.hasNode(self.attrs.main.parent):
			head = self.graph.main.getNode(self.attrs.main.parent)
		else:
			head = Node(self.attrs.main.parent)

		if self.graph.main.hasNode(self.attrs.main.child):
			tail = self.graph.main.getNode(self.attrs.main.child)
		else:
			tail = Node(self.attrs.main.child)

		e = FrameworkEdge(tail, head)

		e.setConditional(self.attrs.main.default.cond)
				
		e.setRoll(self.roll)
		self.graph.main.addEdge(e)


	# <graph>

	def startElement_graph(self, name, attrs):
		if attrs.get('roll'):
			self.roll = attrs.get('roll')
		else:
			self.roll = 'base'

	# <head>

	def startElement_head(self, name, attrs):
		self.text		= ''
		self.attrs.order.gen	= self.attrs.order.default.gen
		
		if attrs.has_key('gen'):
			self.attrs.order.gen = attrs['gen']


	def endElement_head(self, name):
		self.attrs.order.head = self.text
		self.addOrder()
		self.attrs.order.head = None


	# <tail>

	def startElement_tail(self, name, attrs):
		self.text		= ''
		self.attrs.order.gen	= self.attrs.order.default.gen

		if attrs.has_key('gen'):
			self.attrs.order.gen = attrs['gen']

	def endElement_tail(self, name):
		self.attrs.order.tail = self.text
		self.addOrder()
		self.attrs.order.tail = None


	# <to>

	def startElement_to(self, name, attrs):	
		self.text		= ''

		arch = None
		osname = None
		release	= None
		cond = self.attrs.main.default.cond

		if attrs.has_key('arch'):
			arch = attrs['arch']
		if attrs.has_key('os'):
			osname = attrs['os']
			if osname == 'linux':
				osname = 'redhat'
		if attrs.has_key('release'):
			release = attrs['release']
		if attrs.has_key('cond'):
			cond = "( %s and %s )" % (cond, attrs['cond'])
			
		self.attrs.main.cond = \
			stack.cond.CreateCondExpr(arch, osname, release, cond)

	def endElement_to(self, name):
		if (not self.prune) or \
			stack.cond.EvalCondExpr(self.attrs.main.cond, self.attributes):
			self.attrs.main.parent = self.text
			self.addEdge()	
		self.attrs.main.parent = None

	# <from>

	def startElement_from(self, name, attrs):
		self.text		= ''

		arch = None
		osname = None
		release	= None
		cond = self.attrs.main.default.cond

		if attrs.has_key('arch'):
			arch = attrs['arch']
		if attrs.has_key('os'):
			osname = attrs['os']
			if osname == 'linux':
				osname = 'redhat'
		if attrs.has_key('release'):
			release = attrs['release']
		if attrs.has_key('cond'):
			cond = "( %s and %s )" % (cond, attrs['cond'])
			
		self.attrs.main.cond = \
			stack.cond.CreateCondExpr(arch, osname, release, cond)


	def endElement_from(self, name):
		if (not self.prune) or \
			stack.cond.EvalCondExpr(self.attrs.main.cond, self.attributes):
			self.attrs.main.child = self.text
			self.addEdge()	
		self.attrs.main.child = None
		
	# <order>

	def startElement_order(self, name, attrs):
		if attrs.has_key('head'):
			self.attrs.order.head = attrs['head']
		else:
			self.attrs.order.head = None
		if attrs.has_key('tail'):
			self.attrs.order.tail = attrs['tail']
		else:
			self.attrs.order.tail = None
		if attrs.has_key('gen'):
			self.attrs.order.default.gen = attrs['gen']
		else:
			self.attrs.order.default.gen = None
		self.attrs.order.gen = self.attrs.order.default.gen
			
	def endElement_order(self, name):
		if self.attrs.order.head and self.attrs.order.tail:
			self.addOrder()



	# <edge>
	
	def startElement_edge(self, name, attrs):
		if attrs.has_key('arch'):
			arch = attrs['arch']
		else:
			arch = None
		if attrs.has_key('os'):
			osname = attrs['os']
			if osname == 'linux':
				osname = 'redhat'
		else:
			osname = None
		if attrs.has_key('release'):
			release = attrs['release']
		else:
			release	= None
		if attrs.has_key('cond'):
			cond = attrs['cond']
		else:
			cond = None

		self.attrs.main.default.cond = \
			stack.cond.CreateCondExpr(arch, osname, release, cond)
		
		if attrs.has_key('to'):
			self.attrs.main.parent = attrs['to']
		else:
			self.attrs.main.parent = None
		if attrs.has_key('from'):
			self.attrs.main.child = attrs['from']
		else:
			self.attrs.main.child = None

		self.attrs.main.cond	= self.attrs.main.default.cond

	def endElement_edge(self, name):
		if self.attrs.main.parent and self.attrs.main.child:
			self.addEdge()



	def startElement(self, name, attrs):
		try:
			func = getattr(self, "startElement_%s" % name)
		except AttributeError:
			return
		func(name, attrs)


	def endElement(self, name):
		try:
			func = getattr(self, "endElement_%s" % name)
		except AttributeError:
			return
		func(name)

		
	def endDocument(self):
		pass


	def characters(self, s):
		self.text = self.text + s
		


class Pass1NodeHandler(handler.ContentHandler,
	handler.DTDHandler,
	handler.EntityResolver,
	handler.ErrorHandler,
	AttributeHandler):

	"""Sax Parser for the Kickstart Node files"""

	def __init__(self, node, filename, entities, attrs, eval=0, rcl=None):
		handler.ContentHandler.__init__(self)
		self.setAttributes(attrs)
		self.node	= node
		self.entities	= entities
		self.evalShell	= None
		self.evalText	= []
		self.rclCommand = None
		self.rclArgs	= []
		self.copyData	= None
		self.doEval	= eval
		self.doCopy	= eval
		self.rcl	= rcl
		self.xml	= []
		self.filename	= filename
		self.stripText  = 0
		self.attributes = attrs
                self.osname     = attrs['os']


                

	def evalCond(self, attrs):
		arch = None
		osname = None
		release	= None
		cond = None

		if attrs.has_key('arch'):
			arch = attrs['arch']
		if attrs.has_key('os'):
			osname = attrs['os']
			if osname == 'linux':
				osname = 'redhat'
		if attrs.has_key('release'):
			release = attrs['release']
		if attrs.has_key('cond'):
			cond = "( %s and %s )" % (cond, attrs['cond'])

		self.cond = stack.cond.CreateCondExpr(arch, osname, release, cond)
		return stack.cond.EvalCondExpr(self.cond, self.attributes)

	def startElement_description(self, name, attrs):
		self.stripText = 1

	def endElement_description(self, name):
		pass

	def startElement_changelog(self, name, attrs):
		self.stripText = 1

	def endElement_changelog(self, name):
		pass

	def startElement_copyright(self, name, attrs):
		self.stripText = 1

	def endElement_copyright(self, name):
		pass

	def startElement_si_copyright(self, name, attrs):
		self.stripText = 1

	def endElement_si_copyright(self, name):
		pass
	
	# <kickstart> -- or whatever the outermost tag is (os dependent)
	
	def startElement_kickstart(self, name, attrs):
	
		# Setup the Node object to know what roll and what filename 
		# this XML came from.  We use this on the second pass to
		# annotated every XML tag with this information
		palletname = attrs.get('roll')
		
		if not palletname:
			#
			# let's see if the roll (pallet) name is inside the
			# filename
			#
			if self.filename.startswith('/export/stack/pallets'):
				p = self.filename.split('/')
				palletname = p[4]

		if not palletname:
			palletname = 'unknown'

		self.node.setRoll(palletname)

		# Rolls can define individual nodes to be "interface=public".
		# All this does is change the shape of the node on the
		# kickstart graph.  This helps define well know grafting
		# points inside the graph (for example, in the base roll).
 
		if attrs.get('interface'):
			self.node.setShape('box')
		else:
			self.node.setShape('ellipse')
 
		if attrs.get('color'):
			self.node.setFillColor(attrs.get('color'))

		self.node.setFilename(self.filename)
		self.startElementDefault(name, attrs)
			

	# <include>

	def startElement_include(self, name, attrs):
		filename = attrs.get('file')
		if attrs.get('mode'):
			mode = attrs.get('mode')
		else:
			mode = 'quote'

		file = open(os.path.join('include', filename), 'r')
		for line in file.readlines():
			if mode == 'quote':
				if os.environ.has_key('STACKDEBUG'):
					sys.stderr.write('[include]%s' %
						saxutils.escape(line))
				self.xml.append(saxutils.escape(line))
			else:
				if os.environ.has_key('STACKDEBUG'):
					sys.stderr.write('[include]%s' % line)
				self.xml.append(line)
		file.close()

	def endElement_include(self, name):
		pass
	
	# <sinclude> - same as include but allows for missing files

	def startElement_sinclude(self, name, attrs):
		try:
			self.startElement_include(name, attrs)
		except IOError:
			return

	def endElement_sinclude(self, name):
		pass

	# <var>

	def startElement_var(self, name, attrs):
		varName = attrs.get('name')
		varRef  = attrs.get('ref')
		varVal  = attrs.get('val')

		if varVal:
			self.entities[varName] = varVal
		elif varRef:
			if self.entities.has_key(varRef):
				self.entities[varName] = self.entities[varRef]
			else:
				self.entities[varName] = ''
		elif varName:
			#
			# if the entity value is 'None', then we must set
			# it to the empty string. this is because the
			# 'escape' method throws an exception when it
			# tries to XML escape a None type.
			#
			x = self.entities.get(varName)
			if not x:
				x = ''
			
			self.xml.append(saxutils.escape(x))

	def endElement_var(self, name):
		pass

	# <copy>

	def startElement_copy(self, name, attrs):
		if not self.evalCond(attrs):
			self.stripText = 1
			return
		if not self.doCopy:
			return
		if attrs.get('src'):
			src = attrs.get('src')
		if attrs.get('dst'):
			dst = attrs.get('dst')
		else:
			dst = src
		tmpfile = '/tmp/kpp.base64'
		self.xml.append('<file name="%s"/>\n' % dst)
		self.xml.append('<file name="%s">\n' % tmpfile)
		try:
			file = open(src, 'r')
			data = base64.encodestring(file.read())
			file.close()
		except IOError:
			data = ''
		self.xml.append(data)
		self.xml.append('</file>\n')
		self.xml.append("cat %s | /opt/stack/bin/python -c '" % tmpfile)
		self.xml.append('\nimport base64\n')
		self.xml.append('import sys\n')
		self.xml.append("base64.decode(sys.stdin, sys.stdout)' > %s\n"
			 % (dst))
		self.xml.append('rm -rf /tmp/kpp.base64\n')
		self.xml.append('rm -rf /tmp/RCS/kpp.base64,v\n')

	def endElement_copy(self, name):
		pass

	# <report>
	def startElement_report(self, name, attrs):
		self.doReport = True
		if not self.evalCond(attrs):
			self.stripText = 1
			self.doReport = False
			return
		if not self.doEval or not self.rcl:
			return
		if attrs.get('name'):
			self.rclCommand = 'report.%s' % attrs.get('name')


	def endElement_report(self, name):
		if not self.doReport:
			return
		if not self.doEval or not self.rcl:
			return
		result = self.rcl.command(self.rclCommand, self.rclArgs)
		self.xml.append(result)
		self.rclArgs    = []
		self.rclCommand = None

	# <eval>
	
	def startElement_eval(self, name, attrs):
		self.setEvalState = True
		if not self.evalCond(attrs):
			self.setEvalState = False
			self.stripText = 1
			return
		if not self.doEval:
			return
		if attrs.get('shell'):
			self.evalShell = attrs.get('shell')
		else:
			self.evalShell = 'sh'
		if attrs.get('mode'):
			self.evalMode = attrs.get('mode')
		else:
			self.evalMode = 'quote'

		# Special case for python: add the applets directory
		# to the python path.

		if self.evalShell == 'python':
			self.evalShell = os.path.join(os.sep,
				'opt', 'stack', 'bin', 'python')
			self.evalText = ['import sys\nimport os\nsys.path.append(os.path.join("include", "applets"))\n']
			
		
	def endElement_eval(self, name):
		if not self.setEvalState:
			return
		if not self.doEval:
			return

#		for line in string.join(self.evalText, '').split('\n'):
#			if line:
#				if line.find('/opt/stack/bin/stack') == 0:
#					rcl = line
#				else:
#					rcl = None
#		if rcl:
#			rcl = rcl[len('/opt/stack/bin/stack '):]
#			print 'QQQ', rcl
			
		for key in self.entities.keys():
			os.environ[key] = self.entities[key]
			
		r, w = popen2.popen2(self.evalShell)

		if os.environ.has_key('STACKDEBUG'):
			for line in string.join(self.evalText, '').split('\n'):
				sys.stderr.write('[eval]%s\n' % line)
		
		for line in self.evalText:
			w.write(line)
		w.close()

		for line in r.readlines():
			if self.evalMode == 'quote':
				self.xml.append(saxutils.escape(line))
			else:
				self.xml.append(line)
		self.evalText  = []
		self.evalShell = None


	# <post>

	def startElement_post(self, name, attrs):
		self.xml.append('\n'
			'<post>\n'
			'<file name="/var/log/stack-install.log" mode="append">\n'
			'%s: begin post section\n'
			'</file>\n'
			'</post>\n'
			'\n' %
			self.node.getFilename())
		self.startElementDefault(name, attrs)

	def endElement_post(self, name):
		self.endElementDefault(name)
		self.xml.append('\n'
			'<post>\n'
			'<file name="/var/log/stack-install.log" mode="append">\n'
			'%s: end post section\n'
			'</file>\n'
			'</post>\n'
			'\n' %
			self.node.getFilename())

	# <*>

	def startElementDefault(self, name, attrs):
		s = ''
		for attrName in attrs.getNames():
			if attrName not in [ 'roll', 'file' ]:
				attrValue = attrs.get(attrName)
				s += ' %s="%s"' % (attrName, attrValue)
		if not s:
			self.xml.append('<%s>' % name)
		else:
			self.xml.append('<%s %s>' % (name, s))
		
	def endElementDefault(self, name):
		self.xml.append('</%s>' % name)


		
	def startElement(self, name, attrs):
                if name == self.osname:
			func = getattr(self, "startElement_kickstart")
                else:
                        try:
                                func = getattr(self, "startElement_%s" % name)
                        except AttributeError:
                                self.startElementDefault(name, attrs)
                                return
		func(name, attrs)


	def endElement(self, name):
		try:
			func = getattr(self, "endElement_%s" % name)
		except AttributeError:
			self.endElementDefault(name)
			return
		func(name)
		self.stripText = 0

	def characters(self, s):
		if self.stripText:
			return

		if self.rclCommand:
			self.rclArgs.append(s)
		elif self.evalShell:
			self.evalText.append(s)
		else:
			self.xml.append(saxutils.escape(s))
			
	def getXML(self):
		return self.getXMLHeader() + string.join(self.xml, '')


class Pass2NodeHandler(handler.ContentHandler,
	handler.DTDHandler,
	handler.EntityResolver,
	handler.ErrorHandler,
	AttributeHandler):

	"""Sax Parser for XML before it is written to stdout.
	All generated XML is filtered through this to append the file and
	roll attributes to all tags.  The includes tags generated from eval
	and include sections."""
		

	def __init__(self, node, attrs):
		handler.ContentHandler.__init__(self)
		self.setAttributes(attrs)
		self.node = node
		self.xml = []
		self.kstags  = {}
		self.kskey = None
		self.kstext = []
                self.osname = attrs['os']

	def startElement(self, name, attrs):
		self.kstext = []
		
		if name == 'kickstart' or name == self.osname:
			return
		
		if name in [ 'url', 'lang', 'keyboard', 'text', 'reboot',
				'unsupported_hardware' ]:
			self.kskey = name
		else:
			self.kskey = None
						
		s = ''
		for attrName in attrs.getNames():
			attrValue = attrs.get(attrName)
			s += ' %s="%s"' % (attrName, attrValue)
		if 'pallet' not in attrs.getNames():
			s += ' pallet="%s"' % self.node.getRoll()
		if 'file' not in attrs.getNames():
			s += ' file="%s"' % self.node.getFilename()
		if 'color' not in attrs.getNames():
			s += ' color="%s"' % self.node.getFillColor()


		self.xml.append('<%s%s>' % (name, s))
		
	def endElement(self, name):
		if name == 'kickstart' or name == self.osname:
			return

		if self.kskey:
			if not self.kstags.has_key(self.kskey):
				self.kstags[self.kskey] = []
			self.kstags[self.kskey].append(
				string.join(self.kstext, ''))
			
		self.xml.append('</%s>' % name)

	def characters(self, s):
		self.kstext.append(s)
		self.xml.append(saxutils.escape(s))
		
	def getKSText(self):
		text = ''
		for key, val in self.kstags.items():
			for v in val:
				text += '%s %s\n' % (key, v)
		return text
		
	def getXML(self):
		return string.join(self.xml, '')

	
				
				
class Node(stack.graph.Node):

	def __init__(self, name):
		stack.graph.Node.__init__(self, name)
		self.color	= 'black'
		self.fillColor	= 'white'
		self.shape	= 'ellipse'
		self.roll	= ''
		self.filename	= ''
		self.xml	= []
		self.kstext	= []

	def setColor(self, color):
		self.color = color

	def setFilename(self, filename):
		self.filename = filename
	
	def setFillColor(self, color):
		self.fillColor = color
		
	def setShape(self, shape):
		self.shape = shape

	def setRoll(self, name):
		self.roll = name
	
	def addKSText(self, text):
		self.kstext.append(text)
			
	def addXML(self, xml):
		self.xml.append(xml)
		
	def getFilename(self):
		return self.filename
		
	def getRoll(self):
		return self.roll

	def getXML(self):
		return string.join(self.xml, '')

	def getKSText(self):
		return string.join(self.kstext, '')

	def getFillColor(self):
		return self.fillColor

	def getDot(self, prefix='', namespace=''):
		attrs = 'style=filled '
		attrs = attrs + 'shape=%s '     % self.shape
		attrs = attrs + 'label="%s" '   % self.name
		attrs = attrs + 'fillcolor=%s ' % self.fillColor
		attrs = attrs + 'color=%s'      % self.color
		if namespace:
			name = '%s-%s' % (namespace, self.name)
		else:
			name = self.name
		return '%s"%s" [%s];' % (prefix, name, attrs)
		
	def drawDot(self, prefix=''):
		print(self.getDot(prefix))
		

class Edge(stack.graph.Edge):
	def __init__(self, a, b):
		stack.graph.Edge.__init__(self, a, b)
		self.roll	= ''
		self.color	= 'black'
		self.style	= ''

	def setStyle(self, style):
		self.style = style
		
	def setColor(self, color):
		self.color = color

	def setRoll(self, name):
		self.roll = name
		
	def getRoll(self):
		return self.roll

		

class FrameworkEdge(Edge):
	def __init__(self, a, b):
		Edge.__init__(self, a, b)
		self.cond	= None

	def setConditional(self, cond):
		self.cond = cond
		
	def getConditional(self):
		return self.cond

	def getDot(self, prefix=''):
		attrs = ''
		attrs += 'style=%s ' % self.style
		attrs += 'color=%s ' % self.color

		if not self.cond:
			return '%s"%s" -> "%s" ' \
				'[%s arrowsize=1.5];' % (prefix,
				self.parent.name, self.child.name, attrs)

		list = [] 
		label = self.cond.replace('"', '\\"')
		list.append('%s"%s_%s_%s" '
			'[ shape=none label="%s" ];' %
			(prefix, self.parent.name, self.child.name,
			label, label))
		list.append('%s"%s" -> "%s_%s_%s" [%s arrowsize=0];' %
			(prefix, self.parent.name,
			self.parent.name, self.child.name, label,
			attrs))
		list.append('%s"%s_%s_%s" -> "%s" [%s arrowsize=1.5];' %
			(prefix,
			self.parent.name, self.child.name, label,
			self.child.name, attrs))
		return string.join(list, '\n')
					
	
	def drawDot(self, prefix=''):
		print(self.getDot(prefix))
		


class OrderEdge(Edge):
	def __init__(self, head, tail, gen=None):
		Edge.__init__(self, head, tail)
		self.gen = gen

	def getGenerator(self):
		return self.gen

	def getDot(self, prefix='', namespace=''):
		attrs = ''
		attrs = attrs + 'style=%s ' % self.style
		attrs = attrs + 'color=%s ' % self.color
		attrs = attrs + 'arrowsize=1.5'
		if namespace:
			child  = '%s-%s' % (namespace, self.child.name)
			parent = '%s-%s' % (namespace, self.parent.name)
		else:
			child  = self.child.name
			parent = self.parent.name
		return '%s"%s" -> "%s" [%s];' % (prefix, parent, child, attrs)

	def drawDot(self, prefix=''):
		print(self.getDot(prefix))
		


class FrameworkIterator(stack.graph.GraphIterator):
	def __init__(self, graph):
		stack.graph.GraphIterator.__init__(self, graph)
		self.nodes = {}

	def run(self, node):
		stack.graph.GraphIterator.run(self, node)
		keys = self.nodes.keys()
		keys.sort()
		list = []
		for key in keys:
			list.append(self.nodes[key])
		return list
	
	def visitHandler(self, node, edge):
		stack.graph.GraphIterator.visitHandler(self, node, edge)
		if edge:
			cond	= edge.getConditional()
		else:
			cond	= None
		self.nodes[node.name] = (node, cond)


class OrderIterator(stack.graph.GraphIterator):
	def __init__(self, graph):
		stack.graph.GraphIterator.__init__(self, graph)
		self.nodes = []
		self.mark  = {}

	def run(self):

		# First pass: Mark all nodes that have a path to HEAD.
		# We do this by reversing all edges in the graph, and
		# marking all nodes in HEAD's subtree.  Then for all
		# the unmarked nodes create an edge from HEAD to the
		# node.  This will force the HEAD node to be as close
		# as possible to the front of the topological order.

		self.nodes = []		# We don't really use these but we
		self.time  = 0		# might as well intialize them
		for node in self.graph.getNodes():
			self.mark[node] = 0
		self.graph.reverse()
		head = self.graph.getNode('HEAD')
		stack.graph.GraphIterator.run(self, head)
		self.graph.reverse()	# restore edge order

		for node in self.graph.getNodes():
			if not self.mark[node] and node.getInDegree() == 0:
				self.graph.addEdge(OrderEdge(head, node))

		
		# Second pass: Mask all nodes reachable from TAIL.
		# Then for all the unmarked nodes create an edge from
		# TAIL to the node.  This will force TAIL to be as
		# close as possible to the end of the topological
		# order.

		self.nodes = []		# We don't really use these but we
		self.time  = 0		# might as well intialize them
		for node in self.graph.getNodes():
			self.mark[node] = 0
		tail = self.graph.getNode('TAIL')
		stack.graph.GraphIterator.run(self, tail)

		for node in self.graph.getNodes():
			if not self.mark[node] and node.getOutDegree() == 0:
				self.graph.addEdge(OrderEdge(node, tail))
		

		# Third pass: Traverse the entire graph and compute
		# the finishing times for each node.  The reverse sort
		# of the finishing times produces the topological
		# ordering of the graph.  This ordered list of nodes
		# satisifies all of the dependency edges.
		
		self.nodes = []
		self.time  = 0
		stack.graph.GraphIterator.run(self)

		list = []
		self.nodes.sort()
		for rank, node, gen in self.nodes:
			list.append((node, gen))
		list.reverse()

		return list


	def visitHandler(self, node, edge):
		stack.graph.GraphIterator.visitHandler(self, node, edge)
		self.mark[node] = 1
		self.time = self.time + 1

	def finishHandler(self, node, edge):
		stack.graph.GraphIterator.finishHandler(self, node, edge)
		self.time = self.time + 1
		if edge:
			gen = edge.getGenerator()
		else:
			gen = None
		self.nodes.append((self.time, node, gen))

