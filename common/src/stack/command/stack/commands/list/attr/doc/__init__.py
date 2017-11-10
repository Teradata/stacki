# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import fnmatch
import stack.commands
from stack.exception import CommandError


class Command(stack.commands.Command):
	"""
	Lists the set of global attributes.

	<param type='string' name='attr'>
	A shell syntax glob pattern to specify to attributes to
	be listed.
	</param>

	<example cmd='list attr doc'>
	List the documentation for all attributes.
	</example>
	"""

	def run(self, params, args):

		(glob, ) = self.fillParams([ 
			('attr',   None),
		])
		all_attrs = {row[0]: row[1] for row in self.db.select("""
                        attr, doc from attributes_doc
                        """)}

		attrs = {}
		if glob:
			for key in fnmatch.filter(all_attrs.keys(), glob):
				attrs[key] = all_attrs[key]
		else:
			attrs = all_attrs

		self.beginOutput()

		for attr, doc in attrs.items():
			self.addOutput(attr, doc)
					
		self.endOutput(header=['attr', 'doc'])


