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


import stack.commands
from stack.exception import ArgUnique, CommandError


class command(stack.commands.ApplianceArgumentProcessor,
	stack.commands.add.command):
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

		(node, public) = self.fillParams([
			('node', None),
			])

		public = self.bool2str(self.str2bool(public))

		if self.db.count('(ID) from appliances where name=%s', (appliance,)) > 0:
			raise CommandError(self, 'appliance "%s" already exists' % appliance)

		self.db.execute("""
			insert into appliances (name, node)
			values (%s, %s)
			""", (appliance, node))

		# by default, appliances shouldn't be managed or kickstartable...
		implied_attrs = {'managed': False}

		# ... but if the user specified node, they probably want those to be True
		if node:
			self.command('add.appliance.attr', [ appliance,
				'attr=node', 'value=%s' % node ])
			implied_attrs['managed'] = True

		for attr, value in implied_attrs.items():
			self.command('add.appliance.attr', [
				appliance,
				'attr=%s' % attr,
				'value=%s' % value
				])
