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


from stack.argument_processors.appliance import ApplianceArgProcessor
import stack.commands
from stack.exception import ArgUnique, CommandError


class command(ApplianceArgProcessor, stack.commands.add.command):
	pass


class Command(command):
	"""
	Add an appliance specification to the database.

	<arg type='string' name='appliance'>
	The appliance name (e.g., 'backend', 'frontend', 'nas').
	</arg>

	<param type='string' name='node'>
	The name of the root XML node (e.g., 'backend', 'nas'). If
	not supplied, the node name is set to the appliance name.
	</param>
	"""

	def run(self, params, args):

		if len(args) != 1:
			raise ArgUnique(self, 'appliance')
		appliance = args[0]

		(sux, managed) = self.fillParams([('sux', None),
						  ('managed', None)])
     

		if self.db.count('(ID) from appliances where name=%s', (appliance,)) > 0:
			raise CommandError(self, 'appliance "%s" already exists' % appliance)


		# Default to only setting managed=True when the appliance has a
		# SUX node file to build a profile from, but still allow the
		# user to override this on the command line.
		if managed is None:
			managed = False
			if sux:
				managed = True
			
		self.db.execute("""
			insert into appliances (name, sux, managed)
			values (%s, %s, %s)
			""", (appliance, sux, self.str2bool(managed)))

