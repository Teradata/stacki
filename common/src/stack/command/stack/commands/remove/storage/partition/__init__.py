# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ParamRequired


class Command(stack.commands.remove.command, stack.commands.ScopeParamProcessor):
	"""
	Remove a storage partition configuration from the database.

	<param type='string' name='scope'  optional='0'>
	Zero or one parameter. The parameter is the scope for the provided name
	(e.g., 'os', 'host', 'environment', 'appliance').
	No scope means the scope is 'global', and no name will be accepted.
	</param>

	<arg type='string' name='name' optional='0'>
	This argument can be nothing, a valid 'os' (e.g., 'redhat'), a valid
	appliance (e.g., 'backend'), a valid environment (e.g., 'master_node'
	or a host.
	If nothing is supplied, then the removal will be from global.
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
		(scope, device, mountpoint) = self.fillParams([('scope', 'global'), ('device', None), ('mountpoint', None)])
		if (device is None and mountpoint is None):
			if not args or args[0] != '*':
				raise ParamRequired(self, ('device', 'mountpoint'))
		tableids = self.get_scope_name_tableid(scope, params, args)
		for each_tableid in tableids:

			deletesql = "delete from storage_partition where scope = %s and tableid = %s "
			delete_tuple = (scope, each_tableid)

			if device and device != '*':
				deletesql += " and device = %s"
				delete_tuple += (device,)

			if mountpoint and mountpoint != '*':
				deletesql += " and mountpoint = %s"
				delete_tuple += (mountpoint,)

			self.db.execute(deletesql, delete_tuple)
