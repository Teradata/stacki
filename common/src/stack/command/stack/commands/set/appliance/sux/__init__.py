# @copyright@
# @copyright@

import stack.commands
from stack.exception import ArgRequired, ParamUnique


class Command(stack.commands.set.appliance.command,
	      stack.commands.ApplianceArgumentProcessor):
	"""
	Sets the Stacki Universal XML node file for an appliance. 
	This is the root of the configuration graph that is used 
	to produce a machine profile.

	<arg type='string' name='appliance' optional='0'>
	Name of appliance
	</arg>

	<param type='string' name='sux' optional='0'>
	Name of the SUX file
	</param>
	"""

	def run(self, params, args):
		sux = self.fillParams([	('sux', None, True) ])

		if len(args) == 0:
			raise ArgRequired(self, 'appliance')

		appliance = self.getApplianceNames(args)
		if len(appliance) > 1:
			raise ParamUnique(self, 'appliance')

		self.db.execute(
			'update appliances set sux=%s where name=%s',
			(sux, appliance)
		)

