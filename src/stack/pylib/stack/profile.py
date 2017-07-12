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

import os
import sys
import string
import xml
import socket
import base64
import syslog
import subprocess
import stack.util
import stack.graph
import stack.cond

from xml.sax import saxutils
from xml.sax import handler
from xml.sax import make_parser

StackNSURI   = 'http://www.stacki.com'
StackNSLabel = 'stack'


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
		for k in sorted(attrs.keys()):
			v = attrs[k]
			list.append('\t<!ENTITY %s "%s">\n' % (k, v))
		list.append(']>\n')
		self.header = ' '.join(list)

	def getXMLHeader(self):
		return self.header

	
class GraphHandler(handler.ContentHandler,
		   handler.DTDHandler,
		   handler.EntityResolver,
		   handler.ErrorHandler,
		   AttributeHandler):

	def __init__(self, attrs, prune=True, directories=[ '.' ]):
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

		# Find the xml file for each node in the graph.	 If we
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
			raise stack.util.KickstartNodeError('cannot find node "%s"' % node.name)

		xmlFiles = [ xml[0] ]
		if xml[1]:
			xmlFiles.append(xml[1])
		if xml[2]:
			xmlFiles = [ xml[2] ]

		for xmlFile in xmlFiles:

			xmlFileBasename = os.path.split(xmlFile)[1]
		
			# 1st Pass
			#	- Expand XML Entities
			#	- Expand EVAL tags
			#	- Expand INCLUDE/SINCLUDE tag
			#	- Logging for post sections

			fin = open(xmlFile, 'r')
			parser = make_parser()

			handler_1 = Pass1NodeHandler(node, xmlFile, self.attributes, eval, rcl)
			parser.setContentHandler(handler_1)
			parser.setFeature(handler.feature_namespaces, True)
#			parser.setFeature(handler.feature_namespace_prefixes, True)
			header = handler_1.getXMLHeader()

			if self.os == 'redhat':
				s = 'xmlns="%s" ' % StackNSURI
			else:
				s = ''
			s += 'xmlns:stack="%s" ' % StackNSURI
			s += 'xmlns:config="http://www.suse.com/1.0/configns" '
			s += 'xmlns:xi="http://www.w3.org/2003/XInclude"'
			header += '<stack:ns %s>' % s

			if 'STACKDEBUG' in os.environ:
				i = 1
				for x in header.split('\n'):
					sys.stderr.write('[parse1 %4d]%s\n' % (i, x))
					i += 1
			parser.feed(header)

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
				
				if 'STACKDEBUG' in os.environ:
					sys.stderr.write('[parse1 %4d %s]%s' % (i, 
										xmlFileBasename, 
										line))
					i += 1
				try:
					parser.feed(line)
				except:
					print('XML parse error in ' + \
						'file %s ' % xmlFile + \
						'on line %d\n' % linenumber)
					raise
				
			if 'STACKDEBUG' in os.environ:
				sys.stderr.write('[parse1 %4d]</stack:ns>\n' % i)
			parser.feed('</stack:ns>')
			fin.close()
			
			# 2nd Pass
			#	- Expand XML Entities
			#	- Annotate all tags with FILE attribute
			#	- Strip off KICKSTART tags
			#
			# The second pass is required since EVAL tags can
			# create their own XML, instead of requiring the
			# user to annotate we do it for them.
			
			parser = make_parser()
			xml = handler_1.getXML()

			handler_2 = Pass2NodeHandler(node, self.attributes)
			parser.setContentHandler(handler_2)
			parser.setFeature(handler.feature_namespaces, True)
#			parser.setFeature(handler.feature_namespace_prefixes, True)
			if 'STACKDEBUG' in os.environ:
				i = 1
				for x in xml.split('\n'):
					sys.stderr.write('[parse2 %4d %s]%s\n' % (i, 
										  xmlFileBasename,
										  x))
					i += 1
			parser.feed(xml)

			# Attach the final XML to the node object so we can
			# find it again.
			node.addNamespaces(handler_2.xmlns)
			node.addXML(handler_2.getXML())
			node.addKSText(handler_2.getKSText())


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
				
		self.graph.main.addEdge(e)


	# <graph>

	def startElement_graph(self, name, attrs):
		pass

	# <head>

	def startElement_head(self, name, attrs):
		self.text		= ''
		self.attrs.order.gen	= self.attrs.order.default.gen
		
		if 'gen' in attrs:
			self.attrs.order.gen = attrs['gen']


	def endElement_head(self, name):
		self.attrs.order.head = self.text
		self.addOrder()
		self.attrs.order.head = None


	# <tail>

	def startElement_tail(self, name, attrs):
		self.text		= ''
		self.attrs.order.gen	= self.attrs.order.default.gen

		if 'gen' in attrs:
			self.attrs.order.gen = attrs['gen']

	def endElement_tail(self, name):
		self.attrs.order.tail = self.text
		self.addOrder()
		self.attrs.order.tail = None


	# <to>

	def startElement_to(self, name, attrs):	
		self.text = ''

		arch	= None
		osname	= None
		release	= None
		cond	= self.attrs.main.default.cond

		if 'arch' in attrs:
			arch = attrs['arch']
		if 'os' in attrs:
			osname = attrs['os']
			if osname == 'linux':
				osname = 'redhat'
		if 'release' in attrs:
			release = attrs['release']
		if 'cond' in attrs:
			cond = "( %s and %s )" % (cond, attrs['cond'])
			
		self.attrs.main.cond = \
			stack.cond.CreateCondExpr(arch, osname, release, cond)

	def endElement_to(self, name):
		if (not self.prune) or stack.cond.EvalCondExpr(self.attrs.main.cond, self.attributes):
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

		if 'arch' in attrs:
			arch = attrs['arch']
		if 'os' in attrs:
			osname = attrs['os']
			if osname == 'linux':
				osname = 'redhat'
		if 'release' in attrs:
			release = attrs['release']
		if 'cond' in attrs:
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
		if 'head' in attrs:
			self.attrs.order.head = attrs['head']
		else:
			self.attrs.order.head = None
		if 'tail' in attrs:
			self.attrs.order.tail = attrs['tail']
		else:
			self.attrs.order.tail = None
		if 'gen' in attrs:
			self.attrs.order.default.gen = attrs['gen']
		else:
			self.attrs.order.default.gen = None
		self.attrs.order.gen = self.attrs.order.default.gen
			
	def endElement_order(self, name):
		if self.attrs.order.head and self.attrs.order.tail:
			self.addOrder()



	# <edge>
	
	def startElement_edge(self, name, attrs):
		if 'arch' in attrs:
			arch = attrs['arch']
		else:
			arch = None
		if 'os' in attrs:
			osname = attrs['os']
			if osname == 'linux':
				osname = 'redhat'
		else:
			osname = None
		if 'release' in attrs:
			release = attrs['release']
		else:
			release	= None
		if 'cond' in attrs:
			cond = attrs['cond']
		else:
			cond = None

		self.attrs.main.default.cond = \
			stack.cond.CreateCondExpr(arch, osname, release, cond)
		
		if 'to' in attrs:
			self.attrs.main.parent = attrs['to']
		else:
			self.attrs.main.parent = None
		if 'from' in attrs:
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

	def __init__(self, node, filename, attrs, eval=0, rcl=None):
		handler.ContentHandler.__init__(self)
		self.setAttributes(attrs)
		self.node	= node
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
		self.stripText	= False
		self.attributes = attrs
		self.osname	= attrs['os']
		self.namespaces = {}

	def startPrefixMapping(self, ns, uri):
		self.namespaces[uri] = ns

	def getAttr(self, attrs, key):
		if key in attrs.getQNames():
			return attrs.getValueByQName(key)
		return None

	def evalCond(self, attrs):
		arch	  = self.getAttr(attrs, 'arch')
		osname	  = self.getAttr(attrs, 'os')
		release	  = self.getAttr(attrs, 'release')
		cond	  = self.getAttr(attrs, 'cond')

		if osname == 'linux':
			# Remnant of the Solaris port, keep this for now
			# but it is clearly wrong now the we do Ubuntu and SLES.
			osname = 'redhat'

		return stack.cond.EvalCondExpr(stack.cond.CreateCondExpr(arch, osname, release, cond),
					       self.attributes)


	def startElement_stack_description(self, name, attrs):
		self.stripText = True

	def endElement_stack_description(self, name):
		pass

	def startElement_stack_changelog(self, name, attrs):
		self.stripText = True

	def endElement_stack_changelog(self, name):
		pass

	def startElement_stack_copyright(self, name, attrs):
		self.stripText = True

	def endElement_stack_copyright(self, name):
		pass

	def startElement_stack_si_copyright(self, name, attrs):
		self.stripText = True

	def endElement_stack_si_copyright(self, name):
		pass

	def startElement_stack_ns(self, name, attrs):
		pass

	def endElement_stack_ns(self, name):
		pass
	
	# <include>

	def startElement_stack_include(self, name, attrs):
		filename = self.getAttr(attrs, 'file')
		mode	 = self.getAttr(attrs, 'mode')
		if not mode:
			mode = 'quote'

		file = open(os.path.join('include', filename), 'r')
		for line in file.readlines():
			if mode == 'quote':
				if 'STACKDEBUG' in os.environ:
					sys.stderr.write('[include]%s' %
						saxutils.escape(line))
				self.xml.append(saxutils.escape(line))
			else:
				if 'STACKDEBUG' in os.environ:
					sys.stderr.write('[include]%s' % line)
				self.xml.append(line)
		file.close()

	def endElement_stack_include(self, name):
		pass
	
	# <sinclude> - same as include but allows for missing files

	def startElement_stack_sinclude(self, name, attrs):
		try:
			self.startElement_include(name, attrs)
		except IOError:
			return

	def endElement_stack_sinclude(self, name):
		pass

	# <copy>

	def startElement_stack_copy(self, name, attrs):
		if not self.evalCond(attrs):
			self.stripText = True
			return
		if not self.doCopy:
			return
		src = self.getAttr(attrs, 'src')
		dst = self.getAttr(attrs, 'dst')
		if not dst:
			dst = src

		tmpfile = '/tmp/kpp.base64'
		self.xml.append('<stack:file stack:name="%s"/>\n' % dst)
		self.xml.append('<stack:file stack:name="%s">\n' % tmpfile)
		try:
			file = open(src, 'r')
			data = base64.encodestring(file.read())
			file.close()
		except IOError:
			data = ''
		self.xml.append(data)
		self.xml.append('</stack:file>\n')
		self.xml.append("cat %s | /opt/stack/bin/python3 -c '" % tmpfile)
		self.xml.append('\nimport base64\n')
		self.xml.append('import sys\n')
		self.xml.append("base64.decode(sys.stdin, sys.stdout)' > %s\n"
			 % (dst))
		self.xml.append('rm -rf /tmp/kpp.base64\n')
		self.xml.append('rm -rf /tmp/RCS/kpp.base64,v\n')

	def endElement_stack_copy(self, name):
		pass

	# <report>

	def startElement_stack_report(self, name, attrs):
		self.doReport = True
		if not self.evalCond(attrs):
			self.stripText = True
			self.doReport  = False
			return
		if not self.doEval or not self.rcl:
			return
		command = self.getAttr(attrs, 'name')
		if command:
			self.rclCommand = 'report.%s' % command


	def endElement_stack_report(self, name):
		if not self.doReport:
			return
		if not self.doEval or not self.rcl:
			return
		result = self.rcl.command(self.rclCommand, self.rclArgs)
		self.xml.append(result)
		self.rclArgs	= []
		self.rclCommand = None

	# <eval>
	
	def startElement_stack_eval(self, name, attrs):
		
		self.setEvalState = True
		if not self.evalCond(attrs):
			self.setEvalState = False
			self.stripText = True
			return
		if not self.doEval:
			return
		shell = self.getAttr(attrs, 'shell')
		if shell:
			self.evalShell = shell
		else:
			self.evalShell = 'sh'
		mode = self.getAttr(attrs, 'mode')
		if mode:
			self.evalMode = mode
		else:
			self.evalMode = 'quote'

		# Special case for python: add the applets directory
		# to the python path.

		if self.evalShell == 'python':
			self.evalShell = os.path.join(os.sep,
				'opt', 'stack', 'bin', 'python3')
			self.evalText = ['import sys\nimport os\nsys.path.append(os.path.join("include", "applets"))\n']
			
		
	def endElement_stack_eval(self, name):
		if not self.setEvalState:
			return
		if not self.doEval:
			return


		if 'STACKDEBUG' in os.environ:
			i = 1
			sys.stderr.write('[eval:shell]%s\n' % self.evalShell)
			for line in ''.join(self.evalText).split('\n'):
				sys.stderr.write('[eval:%d]%s\n' % (i, line))
				i += 1


		p = subprocess.Popen([ '%s' % self.evalShell ],
				     stdin  = subprocess.PIPE,
				     stdout = subprocess.PIPE,
				     stderr = subprocess.PIPE)

		s = ''.join(self.evalText)
		out, err = p.communicate(s.encode())

		if self.evalMode == 'quote':
			self.xml.append(saxutils.escape(out.decode()))
		else:
			self.xml.append(out.decode())

		self.evalText  = []
		self.evalShell = None


	# <post>

	def startElement_stack_post(self, name, attrs):
		self.xml.append('\n'
			'<stack:post>\n'
			'<stack:file stack:name="/var/log/stack-install.log" stack:mode="append">\n'
			'%s: begin post section\n'
			'</stack:file>\n'
			'</stack:post>\n'
			'\n' %
			self.node.getFilename())
		self.startElementDefault_stack(name, attrs)

	def endElement_stack_post(self, name):
		self.endElementDefault_stack(name)
		self.xml.append('\n'
			'<stack:post>\n'
			'<stack:file stack:name="/var/log/stack-install.log" stack:mode="append">\n'
			'%s: end post section\n'
			'</stack:file>\n'
			'</stack:post>\n'
			'\n' %
			self.node.getFilename())


	# <*> PASS1

	def startElementDefault_stack(self, name, attrs):
		s = ''
		for attrName in attrs.getQNames():
			if attrName not in [ 'roll', 'file' ]:
				attrValue = attrs.getValueByQName(attrName)
				s += ' stack:%s="%s"' % (attrName, attrValue)
		self.xml.append('<stack:%s%s>' % (name, s))
		
	def endElementDefault_stack(self, name):
		self.xml.append('</stack:%s>' % name)


	def startElementNS(self, x, qname, attrs):

		(uri, name) = x
		if uri == StackNSURI and not qname:
			qname = '%s:%s' % (StackNSLabel, name)

		if uri == StackNSURI and name == 'kickstart':
			name  = 'redhat'
			qname = 'stack:redhat'

		if uri == StackNSURI and name == self.osname:
			s = ''
			self.node.setFilename(self.filename)
			for (key, value) in self.namespaces.items():
				s += ' xmlns:%s="%s"' % (value, key)
			self.xml.append('<%s%s>' % (qname, s))
			return

		func = None
		if uri:
			ns = self.namespaces[uri]
			try:
				func = getattr(self, "startElement_%s_%s" % (ns, name))
			except AttributeError:
				try:
					func = getattr(self, "startElementDefault_%s" % ns)
				except AttributeError:
					pass

		if func:
			func(name, attrs)
		else:
			s = ''
			for attrName in attrs.getQNames():
				attrValue = attrs.getValueByQName(attrName)
				s += ' %s="%s"' % (attrName, attrValue)
			self.xml.append('<%s%s>' % (qname, s))


	def endElementNS(self, x, qname):

		(uri, name) = x
		if uri == StackNSURI and not qname:
			qname = '%s:%s' % (StackNSLabel, name)


		n     = ''
		qname = name
		if uri:
			ns    = self.namespaces[uri]
			qname = '%s:%s' % (ns, name)

		if uri == StackNSURI and name == 'kickstart':
			name  = 'redhat'
			qname = 'stack:redhat'

		func = None
		if uri:
			try:
				func = getattr(self, "endElement_%s_%s" % (ns, name))
			except AttributeError:
				try:
					func = getattr(self, "endElementDefault_%s" % ns)
				except AttributeError:
					pass

		if func:
			func(name)
		else:
			self.xml.append('</%s>' % qname)

		self.stripText = False

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
		return self.getXMLHeader() + ''.join(self.xml)


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
		self.namespaces = {}

	def startPrefixMapping(self, ns, uri):
		self.namespaces[uri] = ns

	def getAttr(self, attrs, key):
		if key in attrs.getQNames():
			return attrs.getValueByQName(key)
		return None

	# PASS2

	def startElementNS(self, x, qname, attrs):

		(uri, name) = x
		if uri == StackNSURI and not qname:
			qname = '%s:%s' % (StackNSLabel, name)

		# Fix case where in 'stack' namespace but the tag
		# doesn't know it.  This happens on XML generated
		# from <eval></eval> sections.

		if uri and len(qname.split(':')) == 1:
			qname = '%s:%s' % (self.namespaces[uri], name)

		if uri == StackNSURI and name == 'kickstart':
			name = self.osname

		if name == self.osname:
			self.xmlns = self.namespaces
			return


		if uri == StackNSURI:

			# This is for the <loader></loader> section
			if name in [ 'url', 
				    'lang', 
				    'keyboard', 
				    'text', 
				    'reboot', 
				    'unsupported_hardware' ]:
				self.kskey  = name
				self.kstext = []
			else:
				self.kskey = None
		else:
			self.kskey = None
						
		s = ''
		for attrName in attrs.getQNames():
			attrValue = attrs.getValueByQName(attrName)
			if attrName not in [ 'stack:file', 'stack:id' ]: # should never happen
				s += ' %s="%s"' % (attrName, attrValue)
		s += ' stack:file="%s"' % self.node.getFilename()

		self.xml.append('<%s%s>' % (qname, s))

		
	def endElementNS(self, x, qname):

		(uri, name) = x
		if uri == StackNSURI and not qname:
			qname = '%s:%s' % (StackNSLabel, name)
		
		ns    = ''
		qname = name
		if uri:
			ns    = self.namespaces[uri]
			qname = '%s:%s' % (ns, name)


		if uri == StackNSURI and name == 'kickstart':
			name = self.osname

		if name == self.osname:
			return

		if uri == StackNSURI and self.kskey:
			if not self.kskey in self.kstags:
				self.kstags[self.kskey] = []
			self.kstags[self.kskey].append(''.join(self.kstext))
			self.kskey = None
			
		self.xml.append('</%s>' % qname)

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
		return ''.join(self.xml)

	
				
				
class Node(stack.graph.Node):

	def __init__(self, name):
		stack.graph.Node.__init__(self, name)
		self.filename	= ''
		self.xml	= []
		self.kstext	= []
		self.namespaces = ''

	def setFilename(self, filename):
		self.filename = filename
	
	def addNamespaces(self, ns):
		self.namespaces = ns

	def addKSText(self, text):
		self.kstext.append(text)
			
	def addXML(self, xml):
		self.xml.append(xml)
		
	def getFilename(self):
		return self.filename
		
	def getXML(self):
		return ''.join(self.xml)

	def getKSText(self):
		return ''.join(self.kstext)

	def getNamespaces(self):
		return self.namespaces

	def getDot(self, prefix='', namespace=''):
		attrs = 'style=filled '
		attrs = attrs + 'shape=ellipse '
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
		return '\n'.join(list)
					
	
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
		list = []
		for key in sorted(self.nodes.keys()):
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
		# marking all nodes in HEAD's subtree.	Then for all
		# the unmarked nodes create an edge from HEAD to the
		# node.	 This will force the HEAD node to be as close
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

