#! /opt/stack/bin/python
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import sys
import subprocess
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
		list.append('<!DOCTYPE stack PUBLIC "stack" "http://www.stacki.com" [\n')
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
		self.xmlns			= ''

		# Should we prune the graph while adding edges or not.
		# Prune is the answer for most cases while traversing
		# the graph. "Do Not Prune" is the answer when pictorial
		# representation of graph is required. 
		self.prune			= prune


	def nsAttrs(self):
		return self.xmlns

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
				file = os.path.join(dir, 'extend-%s.xml' % node.name)
				if os.path.isfile(file):
					xml[1] = file
			if not xml[2]:
				file = os.path.join(dir, 'replace-%s.xml' % node.name)
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
			#	- Logging for post sections

			fin       = open(xmlFile, 'r')
			parser    = make_parser(["stack.expatreader"])
			handler_1 = Pass1NodeHandler(node, xmlFile, self.attributes, eval, rcl)
			parser.setContentHandler(handler_1)
			parser.setFeature(handler.feature_namespaces, True)

			xmlns   = handler_1.nsAttrs()
			header  = handler_1.getXMLHeader()
			header += '<stack:ns %s>' % xmlns

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
					print('XML parse error in file %s on line %d\n' % 
					      (xmlFile, linenumber))
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
			
			parser    = make_parser(["stack.expatreader"])
			xml       = handler_1.getXML()
			handler_2 = Pass2NodeHandler(node, self.attributes)
			parser.setContentHandler(handler_2)
			parser.setFeature(handler.feature_namespaces, True)
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
			node.addXML(handler_2.getXML())
			node.addKSText(handler_2.getKSText())

		self.xmlns = xmlns

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
		

class NodeHandler(handler.ContentHandler,
		  handler.DTDHandler,
		  handler.EntityResolver,
		  handler.ErrorHandler,
		  AttributeHandler):

	def __init__(self, node, attrs):
		handler.ContentHandler.__init__(self)
		self.attributes = attrs
		self.os         = attrs['os']
		self.node	= node
		self.xml	= []
		self.setAttributes(attrs)

	def uri2ns(self, uri):
		lookup = { 'http://www.stacki.com'           : 'stack',
			   'http://www.suse.com/1.0/yast2ns' : 'sles',
			   'http://www.suse.com/1.0/configns': 'config',
			   'http://www.w3.org/2003/XInclude' : 'xi'
		}
		if uri in lookup:
			return lookup[uri]
		return ''

	def nsAttrs(self):
		if self.os == 'redhat':
			attrs = [ 
				'xmlns="http://www.stacki.com"',
			]
		elif self.os == 'sles':
			attrs = [
				'xmlns="http://www.suse.com/1.0/yast2ns"',
				'xmlns:sles="http://www.suse.com/1.0/yast2ns"',
				'xmlns:config="http://www.suse.com/1.0/configns"',
				'xmlns:xi="http://www.w3.org/2003/XInclude"'
			]
		attrs.append('xmlns:stack="http://www.stacki.com"')
		return ' '.join(attrs)

	def getAttr(self, attrs, key):
		if key in attrs.getQNames():
			return attrs.getValueByQName(key)
		return None


	def startElementNS(self, name, qname, attrs):

		(uri, tag) = name
		ns         = self.uri2ns(uri)

		self.startTag(ns, tag, attrs)


	def endElementNS(self, name, qname):

		(uri, tag) = name
		ns         = self.uri2ns(uri)

		self.endTag(ns, tag)



class Pass1NodeHandler(NodeHandler):

	"""Sax Parser for the Kickstart Node files"""

	def __init__(self, node, filename, attrs, eval=0, rcl=None):

		NodeHandler.__init__(self, node, attrs)

		self.evalShell	= None
		self.evalText	= []
		self.rclCommand = None
		self.rclArgs	= []
		self.copyData	= None
		self.doEval	= eval
		self.doCopy	= eval
		self.rcl	= rcl
		self.filename	= filename
		self.stripText	= False

	def evalCond(self, attrs):
		# Do both 'stack:' and '' for NS. See stack_report and stack_eval
		# for background (hint: this hack is going away)
		arch	  = self.getAttr(attrs, 'stack:arch')    or self.getAttr(attrs, 'arch')
		osname	  = self.getAttr(attrs, 'stack:os')      or self.getAttr(attrs, 'os')
		release	  = self.getAttr(attrs, 'stack:release') or self.getAttr(attrs, 'release')
		cond	  = self.getAttr(attrs, 'stack:cond')    or self.getAttr(attrs, 'cond')

		if osname == 'linux':
			# Remnant of the Solaris port, keep this for now
			# but it is clearly wrong now that we do Ubuntu and SLES.
			osname = 'redhat'

		return stack.cond.EvalCondExpr(stack.cond.CreateCondExpr(arch, osname, release, cond),
					       self.attributes)


	def startTag_stack_description(self, ns, tag, attrs):
		self.stripText = True

	def endTag_stack_description(self, ns, tag):
		pass

	def startTag_stack_changelog(self, ns, tag, attrs):
		self.stripText = True

	def endTag_stack_changelog(self, ns, tag):
		pass

	def startTag_stack_copyright(self, ns, tag, attrs):
		self.stripText = True

	def endTag_stack_copyright(self, ns, tag):
		pass

	def startTag_stack_rocks(self, ns, tag, attrs):
		self.stripText = True

	def endTag_stack_rocks(self, ns, tag):
		pass

	def startTag_stack_ns(self, ns, tag, attrs):
		pass

	def endTag_stack_ns(self, ns, tag):
		pass
	

	# <stack:stack>

	def startTag_stack_stack(self, ns, tag, attrs):
		#
		# Add the xmlns back into the outer most tag for the next
		# pass.
		self.node.setFilename(self.filename)
		self.xml.append('<%s:%s %s>' % (ns, tag, self.nsAttrs()))


	# <stack:report>

	def startTag_stack_report(self, ns, tag, attrs):
		self.doReport = True
		if not self.evalCond(attrs):
			self.stripText = True
			self.doReport  = False
			return
		if not self.doEval or not self.rcl:
			return
		# still allow non-namespace xml attributes (deprecated)
		command = self.getAttr(attrs, 'stack:name') or self.getAttr(attrs, 'name')

		self.rclCommand = 'report.%s' % command


	def endTag_stack_report(self, ns, tag):
		if not self.doReport:
			return
		if not self.doEval or not self.rcl:
			return
		result = self.rcl.command(self.rclCommand, self.rclArgs)
		if not result: # do not return None
			result = ''
		self.xml.append(result)
		self.rclArgs	= []
		self.rclCommand = None

	# <stack:eval>
	
	def startTag_stack_eval(self, ns, tag, attrs):
		
		self.setEvalState = True
		if not self.evalCond(attrs):
			self.setEvalState = False
			self.stripText = True
			return
		if not self.doEval:
			return

		# Same as stack_report still allow non-namespace xml
		# attributes, we will kill this off after we know
		# all the code uses stack:
		#
		# No risk here, this is not for tags just attributes
		# w/in our tags.

		shell = self.getAttr(attrs, 'stack:shell') or self.getAttr(attrs, 'shell')
		if shell:
			self.evalShell = shell
		else:
			self.evalShell = 'sh'

		mode = self.getAttr(attrs, 'stack:mode') or self.getAttr(attrs, 'mode')
		if mode:
			self.evalMode = mode
		else:
			self.evalMode = 'stack:quote'

		command = self.getAttr(attrs, 'stack:command') or self.getAttr(attrs, 'command')
		if command:
			self.evalText  = None
			self.evalShell = command


		# Special case for python: add the applets directory
		# to the python path.

		if self.evalShell == 'python':
			self.evalShell = os.path.join(os.sep,
				'opt', 'stack', 'bin', 'python3')
			self.evalText = ['import sys\nimport os\nsys.path.append(os.path.join("include", "applets"))\n']
			
		
	def endTag_stack_eval(self, ns, tag):
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
				     stdin=subprocess.PIPE,
				     stdout=subprocess.PIPE,
				     stderr=subprocess.PIPE)

		s = ''.join(self.evalText)
		out, err = p.communicate(s.encode())

		if self.evalMode == 'quote':
			self.xml.append(saxutils.escape(out.decode()))
		else:
			self.xml.append(out.decode())

		self.evalText  = []
		self.evalShell = None


	# <stack:post>

	def startTag_stack_post(self, ns, tag, attrs):
		self.xml.append('\n'
			'<stack:post>\n'
			'<stack:file stack:name="/var/log/stack-install.log" stack:mode="append">\n'
			'%s: begin post section\n'
			'</stack:file>\n'
			'</stack:post>\n'
			'\n' %
			self.node.getFilename())
		self.startTagDefault_stack(ns, tag, attrs)

	def endTag_stack_post(self, ns, tag):
		self.endTagDefault(ns, tag)
		self.xml.append('\n'
			'<stack:post>\n'
			'<stack:file stack:name="/var/log/stack-install.log" stack:mode="append">\n'
			'%s: end post section\n'
			'</stack:file>\n'
			'</stack:post>\n'
			'\n' %
			self.node.getFilename())

	# <stack:*>

	def startTagDefault_stack(self, ns, tag, attrs):
		s = ''
		for attrName in attrs.getQNames():
			attrValue = attrs.getValueByQName(attrName)
			if ns == 'stack' and attrName.find(':') == -1:
				attrName = 'stack:%s' % attrName
			s += ' %s="%s"' % (attrName, attrValue)
		self.xml.append('<%s:%s%s>' % (ns, tag, s))
		


	# <*>

	def startTagDefault(self, ns, tag, attrs):
		if ns:
			qname = '%s:%s' % (ns, tag)
		else:
			qname = tag
		s = ''
		for attrName in attrs.getQNames():
			attrValue = attrs.getValueByQName(attrName)
			s += ' %s="%s"' % (attrName, attrValue)
		self.xml.append('<%s%s>' % (qname, s))

	###

	def endTagDefault(self, ns, tag):
		if ns:
			qname = '%s:%s' % (ns, tag)
		else:
			qname = tag
		self.xml.append('</%s>' % qname)


	def startTag(self, ns, tag, attrs):
		func = self.startTagDefault
		if ns:
			try:
				func = getattr(self, 'startTag_%s_%s' % (ns, tag))
			except AttributeError:
				func = self.startTagDefault_stack

		func(ns, tag, attrs)


	def endTag(self, ns, tag):

		func = self.endTagDefault
		if ns:
			try:
				func = getattr(self, "endTag_%s_%s" % (ns, tag))
			except AttributeError:
				pass

		func(ns, tag)
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
#		print('getXML:', self.filename)
#		print(self.xml)
#		print(self.getXMLHeader())
		return self.getXMLHeader() + ''.join(self.xml)


class Pass2NodeHandler(NodeHandler):
	"""Sax Parser for XML before it is written to stdout.
	All generated XML is filtered through this to append the file and
	roll attributes to all tags.  The includes tags generated from eval
	and include sections."""
		

	def __init__(self, node, attrs):
		NodeHandler.__init__(self, node, attrs)
		self.kstags = {}
		self.kskey  = None
		self.kstext = []


	def startTag(self, ns, tag, attrs):

		self.kskey = None

		if ns == 'stack':

			if tag == 'stack':
				return

			# This is for the <loader></loader> section			
			#
			# This code is broken because of the stack:native tag.
			# Q: Does it need to be fixed or removed?

			if tag in [ 'url', 
				    'lang', 
				    'keyboard', 
				    'text', 
				    'reboot', 
				    'unsupported_hardware' ]:
				self.kskey  = tag
				self.kstext = []
						
		s = ''
		for attrName in attrs.getQNames():
			attrValue = attrs.getValueByQName(attrName)
			s += ' %s="%s"' % (attrName, attrValue)
		s += ' stack:file="%s"' % self.node.getFilename()
		
		if ns:
			qname = '%s:%s' % (ns, tag)
		else:
			qname = tag
		self.xml.append('<%s%s>' % (qname, s))

		
	def endTag(self, ns, tag):

		if ns == 'stack':

			if tag == 'stack':
				return

			if self.kskey:
				if self.kskey not in self.kstags:
					self.kstags[self.kskey] = []
				self.kstags[self.kskey].append(''.join(self.kstext))
				self.kskey = None

		if ns:
			qname = '%s:%s' % (ns, tag)
		else:
			qname = tag
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
			
	def addXML(self, str):
		self.xml.append(str)
		
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

