# @SI_Copyright@
# @SI_Copyright@


import stack.commands


class command(stack.commands.OSArgumentProcessor, 
	      stack.commands.list.command):
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
			
		self.endOutput(header=['os'])
	
