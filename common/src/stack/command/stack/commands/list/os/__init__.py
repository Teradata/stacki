# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.commands
from stack.commands import OSArgProcessor


class command(OSArgProcessor, stack.commands.list.command):
	pass
	

class Command(command):
	"""
	Lists the OSes defined.
	
	<arg optional='1' type='string' name='os' repeat='1'>
	Optional list of os names.
	</arg>
		
	<example cmd='list os'>
	List all known oses.
	</example>
	"""

	def run(self, params, args):
		
		self.beginOutput()

		for x in self.getOSNames(args):
			self.addOutput(x, None)
			
		self.endOutput(header=['os', None])
	
