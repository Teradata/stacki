# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from xml.sax import make_parser
import stack.commands


class Implementation(stack.commands.Implementation):

	def __init__(self, command):
		stack.commands.Implementation.__init__(self, command)
		self.parser = make_parser(["stack.expatreader"])

	def run(self, args):

		filename = args[0]
		handler  = args[1]
		
		print('XXX', filename)
		self.parser.setContentHandler(handler)
#		print(handler.getXMLHeader())
#		self.parser.feed(handler.getXMLHeader())
		print('ZZZ')
		with open(filename, 'r') as graph:
			for line in graph.readlines():
				print(line[:-1])
				self.parser.feed(line)



		
