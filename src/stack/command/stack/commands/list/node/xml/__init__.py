# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
import socket
import stack
import stack.profile
import stack.commands
from xml.sax import saxutils
from xml.sax import handler
from xml.sax import make_parser

class Command(stack.commands.list.command, stack.commands.BoxArgumentProcessor):
	"""
	Lists the XML configuration information for a host. The graph
	traversal for the XML output is rooted at the XML node file
	specified by the 'node' argument. This command executes the first
	pre-processor pass on the configuration graph, performs all
	variable substitutions, and runs all eval sections.

	<param type='string' name='attrs'>
	A list of attributes. This list must be in python dictionary form,
	e.g., attrs="{ 'os': 'redhat', 'arch' : 'x86_64' }"
	</param>

	<param type='string' name='pallet'>
	If set, only expand nodes from the named pallet. If not
	supplied, then the all pallets are used.
	</param>

	<param type='bool' name='eval'>
	If set to 'no', then don't execute eval sections. If not
	supplied, then execute all eval sections.
	</param>

	<param type='bool' name='missing-check'>
	If set to 'no', then disable errors regarding missing nodes.
	If not supplied, then print messages about missing nodes.
	</param>

	<param type='string' name='gen'>
	If set, the use the supplied argument as the program for the
	2nd pass generator. If not supplied, then use 'kgen'.
	</param>

	<example cmd='list node xml compute'>
	Generate the XML graph starting at the XML node named 'compute.xml'.
	</example>
	"""

	def run(self, params, args):
		(attributes, pallets, evalp, missing, generator) = \
			self.fillParams([
				('attrs', ),
				('pallet', ),
				('eval', 'yes'),
				('missing-check', 'no'),
				('gen', 'kgen')
				])
			
		if pallets:
			pallets = pallets.split(',')

		if attributes:
			try:
				attrs = eval(attributes)
			except:
				attrs = {}
				if os.path.exists(attributes):
					file = open(attributes, 'r')
					for line in file.readlines():
						l = line.split(':', 1)
						if len(l) == 2:
							#
							# key/value pairs
							#
							attrs[l[0].strip()] = \
								l[1].strip()
					file.close()
		else:
			attrs = {}

		#
		# make sure all the attributes are XML escaped including
		# the extra characters that are invalid in an entity
		# value.
		#
		for key in attrs.keys():
			try:
				a = saxutils.escape(attrs[key],
						    {'"': '&#x22;',
						     '%': '&#x25;', 
						     '^': '&#x5E;'})
			except:
				a = attrs[key]
			attrs[key] = a

		if 'os' not in attrs:
			attrs['os'] = self.os

		if 'arch' not in attrs:
			attrs['arch'] = self.arch
			
		if 'hostname' not in attrs:
			attrs['hostname'] = self.db.getHostname()

		if 'graph' not in attrs:
			attrs['graph'] = 'default'
			
		if 'box' not in attrs:
			attrs['box'] = 'default'
			
		if 'membership' not in attrs:
			attrs['membership'] = 'Frontend'
	
		if len(args) != 1:
                        raise ArgRequired(self, 'node')
		root = args[0]

		doEval = self.str2bool(evalp)
		allowMissing = self.str2bool(missing)

		if attrs['os'] == 'sunos':
			starter_tag = "jumpstart"
		else:
			starter_tag = "kickstart"

		import stack

		# Add more values to the attributes
		attrs['version'] = stack.version
		attrs['release'] = stack.release
		attrs['root']	 = root
		
		entities = {}

		# Parse the XML graph files in the chosen directory

		#	
		# get the pallets and carts that are in the box associated
		# with the host
		#	
		items = []
		try:
			for name, version, arch in self.getBoxPallets(
					attrs['box']):
				items.append(os.path.join('/export', 'stack',
					'pallets', name, version, 'redhat', arch))
		except:
			#
			# there is no output from 'getBoxPallets()'.
			# let's assume that the database is down
			# (e.g., we are installing and configuring
			# the frontend's database) and we'll get
			# pallet info from '/tmp/rolls.xml' or
			# '/tmp/pallets.xml'
			#

			import stack.roll

			g = stack.roll.Generator()

			if os.path.exists('/tmp/rolls.xml'):
				g.parse('/tmp/rolls.xml')
			elif os.path.exists('/tmp/pallets.xml'):
				g.parse('/tmp/pallets.xml')

			for pallet in g.rolls:
				(pname, pver, prel, parch, purl, pdiskid) \
					= pallet
				items.append(os.path.join('/export',
					'stack', 'pallets', pname, pver,
					'redhat', parch))

		parser  = make_parser()
		handler = stack.profile.GraphHandler(attrs, entities,
			directories = items)

		for item in items:
			graph = os.path.join(item, 'graph')
			if not os.path.exists(graph):
				continue

			for file in os.listdir(graph):
				base, ext = os.path.splitext(file)
				if ext == '.xml':
					path = os.path.join(graph, file)
					fin = open(path, 'r')
					parser.setContentHandler(handler)
					parser.parse(fin)
					fin.close()

		graph = handler.getMainGraph()
		if graph.hasNode(root):
			root = graph.getNode(root)
		else:
			print('error - node %s in not in graph' % root)
			sys.exit(-1)
				
		nodes = stack.profile.FrameworkIterator(graph).run(root)
		deps  = stack.profile.OrderIterator\
			(handler.getOrderGraph()).run()

		# Initialize the hash table for the framework
		# nodes, and filter out everyone not for our
		# architecture and release.
		#
		# Now test for arbitrary conditionals (cond tag),
		# old arch,os test are part of this now are still supported
		
		nodesHash = {}
		for node,cond in nodes:
			nodesHash[node.name] = node
			if not stack.cond.EvalCondExpr(cond, attrs):
				nodesHash[node.name] = None
			
		# Initialize the hash table for the dependency
		# nodes, and filter out everyone not for our
		# generator type (e.g. 'kgen').

		depsHash = {}
		for node,gen in deps:
			depsHash[node.name] = node
			if gen not in [ None, generator ]:
				depsHash[node.name] = None

		for dep,gen in deps:
			if not nodesHash.get(dep.name):
				depsHash[dep.name] = None

		for node,cond in nodes:
			if depsHash.has_key(node.name):
				nodesHash[node.name] = None

		list = []
		for dep,gen in deps:
			if dep.name == 'TAIL':
				for node,cond in nodes:
					list.append(nodesHash[node.
							      name])
			else:
				list.append(depsHash[dep.name])

		# if there was not a 'TAIL' tag, then add the
		# the nodes to the list here

		for node,cond in nodes:
			if nodesHash[node.name] not in list:
				list.append(nodesHash[node.name])

		# Iterate over the nodes and parse everyone we need
		# to parse.

		parsed = []
		kstext = ''
		for node in list:
			if not node:
				continue

			# When building pallets allowMissing=1 and
			# doEval=0.  This is setup by rollRPMS.py

			# for item in items:
			if 0:
				nodefile = os.path.join(item, 'nodes', node)
				if os.path.exists(nodefile):
					node = nodefile
					break

			if allowMissing:
				try:
					handler.parseNode(node, doEval, self)
				except stack.util.KickstartNodeError:
					pass
			else:
				handler.parseNode(node, doEval, self)
				parsed.append(node)
				kstext += node.getKSText()

		# Now print everyone out with the header kstext from
		# the previously parsed nodes

		self.addText('<?xml version="1.0" standalone="no"?>\n')
		self.addText('<!DOCTYPE rocks-graph [\n')
		keys = attrs.keys()
		keys.sort()
		for k in keys:
			v = attrs[k]
			self.addText('\t<!ENTITY %s "%s">\n' % (k, v))
		self.addText(']>\n')
		d = {}
		for key in attrs.keys():
			d[key] = '&%s;' % key
		self.addText('<%s attrs="%s">\n' % (starter_tag, d))
		if attrs['os'] == 'redhat':
			self.addText('<loader>\n')
			self.addText('%s\n' % saxutils.escape(kstext))
			self.addText('%kgen\n')
			self.addText('</loader>\n')

		for node in parsed:

			# If we are only expanding a pallet subgraph
			# then do not ouput the XML for other nodes
				
			if pallets and node.getRoll() not in pallets:
				continue
				
			try:
				self.addText('%s\n' % node.getXML())
			except Exception as msg:
				raise stack.util.KickstartNodeError, \
				      "in %s node: %s" \
				      % (node, msg)

                # Create profile.cfg file of all the attributes used
                # To create the XML Profile.  Since the DB is on the
                # frontend do this only for non-frontend appliances.
		#
		# Also create a post section to preseed any
		# compiled salt templated on the node.

                if attrs.has_key('appliance') and not \
			attrs['appliance'] == 'frontend':

                        self.addText('<post>\n')
                        self.addText('mkdir -p /opt/stack/etc\n')
                        self.addText('<file name="/opt/stack/etc/profile.cfg" perms="0640">\n')
                        self.addText('[attr]\n')
                        for k in keys:
                                self.addText('%s = %s\n' % (k, attrs[k]))
                        self.addText('</file>\n')
                        self.addText('</post>\n')

			try:
				fin = open(os.path.join(os.sep, 'export', 
							'stack', 'salt', 
							'compiled', 
							attrs['hostname'], 
							'kickstart.xml'), 'r')
			except:
				fin = None
			if fin:
				self.addText('<post>\n')
				for line in fin.readlines():
					self.addText(line)
				self.addText('</post>\n')
                
		self.addText('</%s>\n' % starter_tag)
		
		

