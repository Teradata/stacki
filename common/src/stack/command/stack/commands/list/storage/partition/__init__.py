# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgError, ParamValue


class Command(stack.commands.list.command, stack.commands.ScopeParamProcessor):

	"""
	List the storage partition configuration for one of the following:
	global, os, appliance, environment or host.

	<param type='string' name='scope'  optional='0'>
	Zero or one parameter. The parameter is the scope for the provided name
	(e.g., 'os', 'host', 'environment', 'appliance').
	No scope means the scope is 'global', and no name will be accepted.
	</param>

	<arg type='string' name='name' optional='0'>
	This argument can be nothing, a valid 'os' (e.g., 'redhat'), a valid
	appliance (e.g., 'backend'), a valid environment (e.g., 'master_node'
	or a host.
	If nothing is supplied, then the list will be for global scope.
	</arg>

	<example cmd='list storage partition backend-0-0 scope=host'>
	List host-specific storage partition configuration for backend-0-0.
	</example>

	<example cmd='list storage partition backend scope=appliance'>
	List appliance-specific storage partition configuration for all
	backend appliances.
	</example>

	<example cmd='list storage partition'>
	Lists only global storage partition configuration i.e. configuration
	not associated with a specific host or appliance type.
	</example>

	"""

	def scope_query(self, scope, tableid):
		# If we get called recursively we will be provided a new scope
		base_query = " select p.scope, a.name, p.device, p.mountpoint, p.size, p.fstype, p.options, p.partid from " \
		             "storage_partition as p inner join %s as a on p.tableid=%s where p.scope='%s'"
		order_by =  " order by scope,device,partid,size,fstype"
		needs_id = " and tableid = %s "

		querys = {'global' : "select scope, device, mountpoint, size, fstype, options, partid from storage_partition "
		                     "where scope = 'global'" + order_by,
		          'os' : base_query % ('oses', 'a.id', 'os') + needs_id + order_by,
		          'appliance' : base_query % ('appliances', 'a.id', 'appliance') + needs_id + order_by,
		          'environment' : base_query % ('environments', 'a.id', 'environment') + needs_id + order_by,
		          'host' : base_query % ('nodes', 'a.id', 'host') + needs_id + order_by}

		if scope != 'global':
			return self.db.execute(querys[scope], tableid)
		else:
			return self.db.execute(querys[scope])


	def run(self, params, args):
		scope, = self.fillParams([('scope', 'global')])
		if args == []:
			args = None
		tableids = self.get_scope_name_tableid(scope, params, args, list_call=True)
		self.beginOutput()
		# If we are only looking for one table and If query doesn't have any contents exit
		if len(tableids) == 1:
			if self.scope_query(scope, tableids[0]) == 0:
				return
		# We may have a list of hosts (a:backend), so we need to find the data for all of them
		for each_tableid in tableids:
			self.scope_query(scope, each_tableid)
			for row in self.db.fetchall():
				name = ''
				if scope == 'global':
					sql_scope, device, mountpoint, size, fstype, options, partid = row
				else:
					sql_scope, name, device, mountpoint, size, fstype, options, partid = row

				if size == -1:
					size = 'recommended'
				elif size == -2:
					size = 'hibernation'

				if mountpoint == 'None':
					mountpoint = None

				if fstype == 'None':
					fstype = None

				if partid == 0:
					partid = None

				if scope == 'global':
					self.addOutput(sql_scope, [device, partid, mountpoint, size, fstype, options])
				else:
					self.addOutput(sql_scope, [name, device, partid, mountpoint, size, fstype, options])

		if scope == 'global':
			self.endOutput(header=['scope', 'device', 'partid', 'mountpoint', 'size', 'fstype', 'options'],
				               trimOwner=False)
		else:
			self.endOutput(header=['scope', 'name', 'device', 'partid', 'mountpoint', 'size', 'fstype', 'options'],
			               trimOwner=False)
