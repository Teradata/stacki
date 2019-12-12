# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import ast
import os
import subprocess
import stack
import stack.profile
import stack.commands
from stack.exception import ArgRequired, CommandError
from xml.sax import make_parser
from xml.sax import saxutils


class Command(stack.commands.list.command, 
	      stack.commands.BoxArgumentProcessor):
	"""
	Lists the XML configuration information for a host. The graph
	traversal for the XML output is rooted at the XML node file
	specified by the 'node' argument. This command executes the first
	pre-processor pass on the configuration graph, performs all
	variable substitutions, and runs all eval sections.

	<param type='string' name='attrs'>
	A list of attributes. This list must be in python dictionary form,
	e.g., attrs="{ 'os': 'redhat', 'arch' : 'x86_64' }" or must be a
	file of key:value pairs separated by newlines.
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

	<example cmd='list node xml backend'>
	Generate the XML graph starting at the XML node named 'backend.xml'.
	</example>
	"""

	def run(self, params, args):
		(attributes, pallets, evalp, missing, generator, basedir) = \
			self.fillParams([
				('attrs', ),
				('pallet', ),
				('eval', 'yes'),
				('missing-check', 'no'),
				('gen', 'kgen'),
				('basedir', None),
				])
			
		if pallets:
			pallets = pallets.split(',')

		if attributes:
			try:
				attrs = ast.literal_eval(attributes)
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
		# if there is an empty key in the attrs dictionary, remove
		# it, otherwise it will cause an exception below.
		#
		if '' in attrs.keys():
			del attrs['']

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

		if len(args) != 1:
			raise ArgRequired(self, 'node')
		root = args[0]

		doEval = self.str2bool(evalp)
		allowMissing = self.str2bool(missing)

		# yes, this was already imported above.  Take it out and it crashes looking up .version.
		# First added in commit 38623be.  No one knows why it's needed.
		import stack

		# Add more values to the attributes
		attrs['version'] = stack.version
		attrs['release'] = stack.release
		attrs['root']	 = root
		
		# Parse the XML graph files in the chosen directory

		#	
		# get the pallets that are in the box associated with the host
		#	
		items = []
		try:
			for pallet in self.getBoxPallets(attrs['box']):
				items.append(os.path.join('/export', 'stack', 'pallets',
					pallet.name, pallet.version, pallet.rel, pallet.os, pallet.arch))
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
					'stack', 'pallets', pname, pver, prel,
					self.os, parch))

		#
		# get the carts associated with the box
		#
		output = self.call('list.cart')
		devnull = open('/dev/null', 'w')
		for o in output:
			if attrs['box'] in o['boxes'].split():
				items.append(os.path.join('/export', 'stack',
					'carts', o['name']))
	
				#
				# if a cart has changed since the last time we
				# built a kickstart file, we will need to
				# 'compile' it which may take a long time
				# (because we create a repo in the cart and
				# if there are a lot of RPMS the checksum will
				# take a long time) -- so, let's fork off the
				# cart compilation.
				#
				subprocess.Popen([ '/opt/stack/bin/stack',
					'compile', 'cart', o['name'] ],
					stdout=devnull, stderr=devnull)

		if basedir:
			if os.path.exists(basedir) and os.path.isdir(basedir):
				items = [os.path.realpath(basedir)]

		handler = stack.profile.GraphHandler(attrs, directories=items)

		for item in items:
			graph = os.path.join(item, 'graph')
			if not os.path.exists(graph):
				continue

			for file in os.listdir(graph):
				base, ext = os.path.splitext(file)
				if ext == '.xml':
					parser = make_parser(["stack.expatreader"])
					parser.setContentHandler(handler)
					parser.feed(handler.getXMLHeader())
					linenumber = 0

					with open(os.path.join(graph, file), 'r') as xml:
						for line in xml.readlines():
							linenumber = linenumber + 1
							if line.find('<?xml') != -1:
								continue
							try:
								parser.feed(line)
							except Exception as e:
								print('XML parse error in graph file - %s in file %s on line %d\n' % (e.args[-1], xml.name, linenumber))
								raise


		graph = handler.getMainGraph()
		if graph.hasNode(root):
			root = graph.getNode(root)
		else:
			raise CommandError(self, 'node "%s" not in graph' % root)

		nodes = stack.profile.FrameworkIterator(graph).run(root)
		deps  = stack.profile.OrderIterator(handler.getOrderGraph()).run()

		# Initialize the hash table for the framework
		# nodes, and filter out everyone not for our
		# architecture and release.
		#
		# Now test for arbitrary conditionals (cond tag),
		# old arch,os test are part of this now are still supported
		
		nodesHash = {}
		for node, cond in nodes:
			nodesHash[node.name] = node
			if not stack.cond.EvalCondExpr(cond, attrs):
				nodesHash[node.name] = None
			
		# Initialize the hash table for the dependency
		# nodes, and filter out everyone not for our
		# generator type (e.g. 'kgen').

		depsHash = {}
		for node, gen in deps:
			depsHash[node.name] = node
			if gen not in [ None, generator ]:
				depsHash[node.name] = None

		for dep, gen in deps:
			if not nodesHash.get(dep.name):
				depsHash[dep.name] = None

		for node, cond in nodes:
			if node.name in depsHash:
				nodesHash[node.name] = None

		list = []
		for dep, gen in deps:
			if dep.name == 'TAIL':
				for node, cond in nodes:
					list.append(nodesHash[node.
							      name])
			else:
				list.append(depsHash[dep.name])

		# if there was not a 'TAIL' tag, then add the
		# the nodes to the list here

		for node, cond in nodes:
			if nodesHash[node.name] not in list:
				list.append(nodesHash[node.name])

		# Iterate over the nodes and parse everyone we need
		# to parse.

		parsed     = []
		kstext     = ''
		for node in list:
			if not node:
				continue

			# When building pallets allowMissing=1 and
			# doEval=0.  This is setup by rollRPMS.py

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

		self.addText('<stack:profile stack:os="%s"' % attrs['os'])
		self.addText(' %s' % handler.nsAttrs())
		self.addText(' stack:attrs=%s>\n' % saxutils.quoteattr('%s' % attrs))

		self.runPlugins(attrs)

		for node in parsed:
			# If we are only expanding a pallet subgraph
			# then do not ouput the XML for other nodes

			pallet   = None
			try:
				filename = node.getFilename()
				pallet   = filename.split('pallets')[1].split(os.sep)[1]
			except:
				pass

			if pallets and pallet not in pallets:
				continue
				
			try:
				self.addText('%s\n' % node.getXML())
			except Exception as msg:
				raise stack.util.KickstartNodeError("in %s node: %s" % (node, msg))

		self.addText('</stack:profile>\n')
		
		

