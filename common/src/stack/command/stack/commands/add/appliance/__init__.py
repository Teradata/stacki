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
from stack.commands import ApplianceArgProcessor
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

	<param type='bool' name='public'>
	True means this appliance will be displayed by 'insert-ethers' in
	the Appliance menu. The default is 'yes'.
	</param>

	<example cmd='add appliance nas node=nas public=yes'>
	</example>
	"""

	def run(self, params, args):

		if len(args) != 1:
			raise ArgUnique(self, 'appliance')
		appliance = args[0]

		(node, public) = self.fillParams([
			('node', ''),
			('public', 'y')
			])

		public  = self.bool2str(self.str2bool(public))

		# check for duplicates
		if self.db.count('(ID) from appliances where name=%s', (appliance,)) > 0:
			raise CommandError(self, 'appliance "%s" already exists' % appliance)

		# ok, we're good to go
		self.db.execute('''
			insert into appliances (name, public) values
			(%s, %s)
			''', (appliance, public))

		# by default, appliances shouldn't be managed or kickstartable...
		implied_attrs = {'kickstartable': False, 'managed': False}

		# ... but if the user specified node, they probably want those to be True
		if node:
			self.command('add.appliance.attr', [ appliance,
				'attr=node', 'value=%s' % node ])
			implied_attrs['kickstartable'] = True
			implied_attrs['managed'] = True

		for attr, value in implied_attrs.items():
			self.command('add.appliance.attr', [
				appliance,
				'attr=%s' % attr,
				'value=%s' % value
				])
