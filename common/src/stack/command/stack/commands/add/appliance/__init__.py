# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@


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

	<param type='string' name='longname'>
	The full name of the appliance. This name will be displayed
	in the appliances menu by insert-ethers (e.g., 'backend'). If
	not supplied, the long name is set to the appliance name.
	</param>

	<param type='string' name='node'>
	The name of the root XML node (e.g., 'backend', 'nas'). If
	not supplied, the node name is set to the appliance name.
	</param>

	<param type='bool' name='public'>
	True means this appliance will be displayed by 'insert-ethers' in
	the Appliance menu. The default is 'yes'.
	</param>

	<example cmd='add appliance nas longname="NAS Appliance" node=nas public=yes'>
	</example>
	"""

	def run(self, params, args):

		if len(args) != 1:
			raise ArgUnique(self, 'appliance')
		appliance = args[0]

		(longname, node, public) = self.fillParams([
			('longname', None),
			('node', ''),
			('public', 'y')
			])

		public  = self.bool2str(self.str2bool(public))

		if not longname:
			longname = str.capitalize(appliance)

		#
		# check for duplicates
		#
		rows = self.db.execute("""
			select * from appliances where name='%s'
			""" % appliance)
		if rows > 0:
			raise CommandError(self, 'appliance "%s" already exists' % appliance)

		#
		# ok, we're good to go
		#
		self.db.execute("""
			insert into appliances (name, longname, public) values
			('%s', '%s', '%s')
			""" % (appliance, longname, public))

		if not node:
			kickstartable = False
		else:
			kickstartable = True
			self.command('add.appliance.attr', [ appliance,
				'attr=node', 'value=%s' % node ])

		self.command('add.appliance.attr', [
			appliance,
			'attr=kickstartable',
			'value=%s' % self.bool2str(kickstartable)
			])

