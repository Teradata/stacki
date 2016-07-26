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



import os
import sys
import string
import json
import stack.util
import stack.profile
import stack.graph
import stack.file
import stack.commands
from stack.exception import *

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
	
	<example cmd='list host graph compute-0-0'>
	Generates a graph for compute-0-0
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
			('size','100,100'),
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
								 row['name'], row['version'], row['os'], 
								 row['arch'], 'graph'))

			for row in self.call('list.cart'):
				boxes = row['boxes'].split(' ')
				if box in boxes:
					dirs.append(os.path.join(os.sep, 'export', 'stack', 'carts', 
								 row['name'], 'graph'))

			parser = make_parser()
			attrs = self.db.getHostAttrs(host)
			handler = stack.profile.GraphHandler(attrs, {}, prune=False)

			for dir in dirs:
				if not os.path.exists(dir):
					continue
				for file in os.listdir(dir):
					root, ext = os.path.splitext(file)
					if ext == '.xml':
						path = os.path.join(dir, file)
						if not os.path.isfile(path):
							continue
						fin = open(path, 'r')
						parser.setContentHandler(handler)
						parser.parse(fin)
						fin.close()
			
			if 'type' in params and params['type'] == 'json':
                                dot = self.createJSONGraph(handler)
				self.addOutput(host, dot)
                        else:
                                dot = self.createDotGraph(handler,
                                        self.readDotGraphStyles())
				for line in dot:
					self.addOutput(host, line)

		self.endOutput(padChar='')

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
		dict = {}
		for node in handler.getOrderGraph().getNodes():
			#try:
			#	handler.parseNode(node, 0) # Skip <eval>
			#except stack.util.KickstartNodeError:
			#	pass
			try:
				color = styleMap[node.getRoll()].nodeColor
			except:
				color = 'white'
			node.setFillColor(color)
			dot.append(node.getDot('\t\t', 'order'))

		iter = stack.profile.OrderIterator(handler.getOrderGraph())
		iter.run()

		for e in handler.getOrderGraph().getEdges():
			try:
				color = styleMap[e.getRoll()].edgeColor
				style = 'bold'
			except:
				color = 'black'
				style = 'invis'
			e.setColor(color)
			e.setStyle(style)
			dot.append(e.getDot('\t\t', 'order'))
		dot.append('\t}')

		# Main Graph

		dot.append('\tsubgraph clustermain {')
		dot.append('\t\tlabel="Profile Graph";')
		dot.append('\t\tfontsize=32;')
		dot.append('\t\tcolor=black;')
		for node in handler.getMainGraph().getNodes():
			#try:
			#	handler.parseNode(node, 0) # Skip <eval>
			#except stack.util.KickstartNodeError:
			#	pass
			try:
				color = styleMap[node.getRoll()].nodeColor
			except:
				color = 'white'
			node.setFillColor(color)
			dot.append(node.getDot('\t\t'))
		for e in handler.getMainGraph().getEdges():
			try:
				color = styleMap[e.getRoll()].edgeColor
			except:
				color = 'black'
			e.setColor(color)
			e.setStyle('bold')
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
			tokens = string.split(name, '-')
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
				map[r].edgeColor = h.getEdgeColor()
				map[r].nodeColor = h.getNodeColor()
				map[r].nodeShape = h.getNodeShape()

		return map

