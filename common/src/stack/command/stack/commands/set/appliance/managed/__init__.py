# @copyright@
# @copyright@

import stack.commands
from stack.exception import ArgRequired, ParamUnique


class Command(stack.commands.set.appliance.command,
	      stack.commands.ApplianceArgumentProcessor):
	"""
	Sets the Appliance to either managed or unmanaged. 
	Unmanaged appliance are ignored by commands like `run host` and sync.

	<arg type='string' name='appliance' optional='0'>
	Name of appliance
	</arg>

	<param type='bool' name='managed'>
	True or false (defaults to true)
	</param>
	"""

	def run(self, params, args):
		managed, = self.fillParams([ ('managed', True) ])

		if len(args) == 0:
			raise ArgRequired(self, 'appliance')

		appliance = self.getApplianceNames(args)
		if len(appliance) > 1:
			raise ParamUnique(self, 'appliance')

		self.db.execute(
			'update appliances set managed=%s where name=%s',
			(self.str2bool(managed), appliance)
		)

