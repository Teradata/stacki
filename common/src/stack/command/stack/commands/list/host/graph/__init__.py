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
import string
import json
import stack.util
import stack.profile
import stack.graph
import stack.file
import stack.commands

from xml.sax import make_parser


class Command(stack.commands.list.host.command):
	"""
	For each host, output a graphviz script to produce a diagram of the
	XML configuration graph. If no hosts are specified, a graph for every
	known host is listed.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<param type='string' name='arch'>
	Optional. If specified, generate a graph for the specified CPU type.
	If not specified, then 'arch' defaults to this host's architecture.
	</param>

	<param type='string' name='basedir'>
	Optional. If specified, the location of the XML node files.
	</param>
	
	<example cmd='list host graph backend-0-0'>
	Generates a graph for backend-0-0
	</example>
	"""

	def run(self, params, args):
	
		# In the future we should store the ARCH in the database
		# and allow the cgi/url to override the default setting.
		# When this happens we can do a db lookup instead of using
		# a flag and defaulting to the host architecture.

		(arch, basedir, landscape, size) = self.fillParams(
			[('arch', self.arch),
			('basedir', ),
			('landscape', 'n'),
			('size', '100,100'),
			])

		self.beginOutput()
		
		self.drawOrder		= 0
		self.drawKey		= 1
		self.drawLandscape	= self.str2bool(landscape)
		self.drawSize		= size
		
		for host in self.getHostnames(args):

			box = None
			for row in self.call('list.host', [ host ]):
				box = row['box']
			if not box:
				continue

			dirs = []
			for row in self.call('list.pallet'):
				boxes = row['boxes'].split(' ')
				if box in boxes:
					dirs.append(os.path.join(os.sep, 'export', 'stack', 'pallets', 
						 row['name'], row['version'], row['release'], row['os'],
						 row['arch'], 'graph'))

			for row in self.call('list.cart'):
				boxes = row['boxes'].split(' ')
				if box in boxes:
					dirs.append(os.path.join(os.sep, 'export', 'stack', 'carts', 
								 row['name'], 'graph'))

			attrs = {}
			for row in self.call('list.host.attr', [ host ]):
				attrs[row['attr']] = row['value']

			handler = stack.profile.GraphHandler(attrs, prune=False)

			for dir in dirs:
				if not os.path.exists(dir):
					continue
				for file in os.listdir(dir):
					root, ext = os.path.splitext(file)
					if ext == '.xml':
						path = os.path.join(dir, file)
						if not os.path.isfile(path):
							continue
						parser = make_parser(['stack.expatreader'])
						parser.setContentHandler(handler)
						parser.feed(handler.getXMLHeader())
						with open(path, 'r') as xml:
							for line in xml.readlines():
								if line.find('<?xml') != -1:
									continue
								parser.feed(line)
			
			if 'type' in params and params['type'] == 'json':
				dot = self.createJSONGraph(handler)
				self.addOutput(host, dot)
			else:
				dot = self.createDotGraph(handler,
					self.readDotGraphStyles())
				for line in dot:
					self.addOutput(host, line)

		self.endOutput(padChar='', trimOwner=True)

	def createJSONGraph(self, handler):
		"Output JSON format for D3 graph"
		D = []
		#fill array of edge parent and children
		for e in handler.getMainGraph().getEdges():
			D.append({"source": str(e.parent.name), "target": str(e.child.name)})

		return json.dumps(D)	
	
	def createDotGraph(self, handler, styleMap):
		dot = []
		dot.append('digraph rocks {')
		dot.append('\tsize="%s";' % self.drawSize)
		if self.drawLandscape:
			dot.append('\trankdir=TB;')
		else:
			dot.append('\trankdir=LR;')
		# Key
		
		dot.append('\tsubgraph clusterkey {')
		dot.append('\t\tlabel="Rolls";')
		dot.append('\t\tfontsize=32;')
		dot.append('\t\tcolor=black;')
		for key in styleMap:
			a = 'style=filled '
			a += 'shape=%s '    % styleMap[key].nodeShape
			a += 'label="%s" ' % key
			a += 'fillcolor=%s' % styleMap[key].nodeColor
			dot.append('\t\t"roll-%s" [%s];' % (key, a))
		dot.append('\t}')

		# Ordering Graph
		
		dot.append('\tsubgraph clusterorder {')
		dot.append('\t\tlabel="Ordering Contraints";')
		dot.append('\t\tfontsize=32;')
		dot.append('\t\tcolor=black;')

		for node in handler.getOrderGraph().getNodes():
			color = 'white'
			dot.append(node.getDot('\t\t', 'order'))

		iter = stack.profile.OrderIterator(handler.getOrderGraph())
		iter.run()

		for e in handler.getOrderGraph().getEdges():
			color = 'black'
			style = 'bold'
			dot.append(e.getDot('\t\t', 'order'))
		dot.append('\t}')

		# Main Graph

		dot.append('\tsubgraph clustermain {')
		dot.append('\t\tlabel="Profile Graph";')
		dot.append('\t\tfontsize=32;')
		dot.append('\t\tcolor=black;')
		for node in handler.getMainGraph().getNodes():
			color = 'white'
			dot.append(node.getDot('\t\t'))
		for e in handler.getMainGraph().getEdges():
			color = 'black'
			dot.append(e.getDot('\t\t'))
		dot.append('\t}')

#		for mainNode in handler.getMainGraph().getNodes():
#			dot.append('"%s" -> "order-%s" [ style="invis"];' %
#				(mainNode.name,
#				 handler.getOrderGraph().getNode('HEAD')))


		dot.append('}')
		return dot


	def readDotGraphStyles(self):
		p   = make_parser()
		h   = stack.profile.RollHandler()
		map = {}
		
		for file in os.listdir('.'):
			tokens = os.path.splitext(file)
			if len(tokens) != 2:
				continue
			name = tokens[0]
			ext  = tokens[1]
			tokens = name.split('-')
			if len(tokens) < 2:
				continue
			prefix = tokens[0]
			if prefix == 'roll' and \
			   ext == '.xml' and \
			   os.path.isfile(file):
				fin = open(file, 'r')
				p.setContentHandler(h)
				p.parse(fin)
				fin.close()
				r = h.getRollName()
				map[r] = stack.util.Struct()
				map[r].edgeColor = 'black'
				map[r].nodeColor = 'black'
				map[r].nodeShape = 'ellipse'

		return map
