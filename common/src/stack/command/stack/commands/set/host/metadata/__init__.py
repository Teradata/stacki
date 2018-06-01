# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.set.host.command):
	"""
	Set the metadata for a list of hosts. The metadata is
	reserved for the user and is not used internally by Stacki. The
	intention is to provide a mechanism similar to the AWS
	meta-data to allow arbitrary data to be attached to a host.

	It is recommended that the metadata (if used) should be a JSON
	document but there are no assumptions from Stacki on the
	structure of the data.

	Metadata should be accessed using the "metadata" read-only attribute.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='metadata' optional='0'>
	The metadata document
	</param>
	"""

	def run(self, params, args):
		
		(metadata, ) = self.fillParams([
			('metadata', None, True)
			])
		
		if not len(args):
			raise ArgRequired(self, 'host')

		for host in self.getHostnames(args):
			self.db.execute("""
				update nodes set metadata=%s where
				name=%s""",
				(metadata, host))
		
