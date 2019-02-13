# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
import json
import os
import stack.commands
import stack.profile
from xml.sax import make_parser

class Command(stack.commands.Command): 
	"""
	Check all node and graph files across all pallets and carts for XML errors.

	<example cmd='verify xml'>
	List of errors displayed in 3 column format i.e. filename, line number and XML error.
	No output indicates that there are no errors. 
	</example>
	"""

	# Parse and identify XML errors in a directory
	def checkXML(self, dirPath):
		errList = []

		for file in os.listdir(dirPath):
			base, ext = os.path.splitext(file)
			if ext == '.xml':
				parser = make_parser(["stack.expatreader"])
				parser.setContentHandler(self.handler)
				parser.feed(self.handler.getXMLHeader())
				linenumber = 0

				with open(os.path.join(dirPath, file), 'r') as xml:
					for line in xml.readlines():
						linenumber = linenumber + 1

						if line.find('<?xml') != -1:
							continue
						try:
							parser.feed(line)
						except Exception as e:
							errArray = []
							errArray.append(str(xml.name))
							errArray.append(str(linenumber))
							errArray.append(e.args[-1])
							errList.append(errArray)
							break
		return errList

	def run(self, params, args):
		attrs = {}
		attrs['os'] = self.os
		attrs['arch'] = self.arch

		dirPaths = []
		
		# Check XML files in all the pallets across boxes
		pallets = self.call('list.pallet', [ 'output-format=json' ])
		for pallet in pallets:
			name    = pallet['name']
			version = pallet['version']
			rel     = pallet['release']
			arch    = pallet['arch']
			osname  = pallet['os']

			dirPaths.append(os.path.join('/export', 'stack', \
				'pallets', name, version, rel, osname, arch))

		# Check XML files in all the carts
		carts = self.call('list.cart', [ 'output-format=json' ])
		for cart in carts:
			dirPaths.append(os.path.join('/export', 'stack', 'carts', \
				cart['name']))

		self.handler = stack.profile.GraphHandler(attrs, directories=dirPaths)
		
		errList = []
		for dirPath in dirPaths:
			graph = os.path.join(dirPath, 'graph')
			
			if not os.path.exists(graph):
				continue

			node = os.path.join(dirPath, 'nodes')
			errList.extend(self.checkXML(graph))
			errList.extend(self.checkXML(node))

		# Print XML errors in a 3 column format
		if errList:
			header = ['', 'filename', 'linenumber', 'errmessage']
			self.beginOutput()
			for e in errList:
				self.addOutput('', (e[0], e[1], e[2]))
			self.endOutput(header=header, padChar=' ')
