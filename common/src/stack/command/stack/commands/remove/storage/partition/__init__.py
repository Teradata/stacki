# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, ArgError, ParamValue, ParamRequired


class Command(stack.commands.remove.command,
		stack.commands.OSArgumentProcessor,
		stack.commands.HostArgumentProcessor,
		stack.commands.ApplianceArgumentProcessor):
	"""
	Remove a storage partition configuration from the database.

	<param type='string' name='scope' optional='0'>
	Scope of partition definition: a valid os (e.g.,
	'redhat'), a valid appliance (e.g., 'backend') or a valid host
	(e.g., 'backend-0-0). Default scope is 'global'.
	</param>

	<arg type='string' name='name'>
	Zero or one argument of host, appliance or os name
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be removed from
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be removed from
	the database.
	</param>

	<example cmd='remove storage partition backend-0-0 device=sda'>
	Remove the disk partition configuration for sda on backend-0-0.
	</example>

	<example cmd='remove storage partition backend-0-0 device=sda mountpoint=/var'>
	Remove the disk partition configuration for partition /var on sda on backend-0-0.
	</example>

	<example cmd='remove storage partition backend'>
	Remove the disk array configuration for backend
	appliance.
	</example>
	"""

	def run(self, params, args):
		(scope, device, mountpoint) = self.fillParams([
			('scope', 'global'), ('device', None), ('mountpoint', None)])
		oses = []
		appliances = []
		hosts = []
		name = None
		accepted_scopes = ['global', 'os', 'appliance', 'host']

		# Some checking that we got usable input.:
		if scope not in accepted_scopes:
			raise ParamValue(self, '%s' % params, 'one of the following: %s' % accepted_scopes )
		elif scope == 'global' and len(args) >= 1:
			raise ArgError(self, '%s' % args, 'unexpected, please provide a scope: %s' % accepted_scopes)
		elif scope == 'global' and (device is None and mountpoint is None):
			raise ParamRequired(self, 'device OR mountpoint')
		elif scope != 'global' and len(args) < 1:
			raise ArgRequired(self, '%s name' % scope)

		if scope == "os":
			oses = self.getOSNames(args)
		elif scope == "appliance":
			appliances = self.getApplianceNames(args)
		elif scope == "host":
			hosts = self.getHostnames(args)

		if scope != 'global':
			name = args[0]

		#
		# look up the id in the appropriate 'scope' table
		#
		tableid = -1
		tablename = {"os":"oses", "appliance":"appliances", "host":"nodes"}
		if scope != 'global':
			self.db.execute("""select id from %s where
				name = '%s' """ % (tablename[scope], name))
			tableid, = self.db.fetchone()

		deletesql = """delete from storage_partition where
			scope = '%s' and tableid = %s """ % (scope, tableid)

		if device and device != '*':
			deletesql += """ and device = '%s'""" % device

		if mountpoint and mountpoint != '*':
			deletesql += """ and mountpoint = '%s'""" % mountpoint

		self.db.execute(deletesql)
