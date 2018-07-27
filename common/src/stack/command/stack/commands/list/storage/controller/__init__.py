#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.exception import ArgError, ParamValue


class Command(stack.commands.list.command, stack.commands.ScopeParamProcessor):
	"""
	List the storage controller configuration for one of the following:
	global, os, appliance or host.

	<param type='string' name='scope'  optional='0'>
	Zero or one parameter. The parameter is the scope for the provided name
	(e.g., 'os', 'host', 'environment', 'appliance').
	No scope means the scope is 'global', and no name will be accepted.
	</param>

	<arg type='string' name='name' optional='0'>
	This argument can be nothing, a valid 'os' (e.g., 'redhat'), a valid
	appliance (e.g., 'backend'), a valid environment (e.g., 'master_node'
	or a host.
	If nothing is supplied, then the configuration will be global.
	</arg>

	<example cmd='list storage controller backend-0-0 scope=host'>
	List host-specific storage controller configuration for backend-0-0.
	</example>

	<example cmd='list storage controller backend scope=appliance'>
	List appliance-specific storage controller configuration for all
	backend appliances.
	</example>

	<example cmd='list storage controller'>
	List global storage controller configuration.
	</example>

	"""
	def scope_query(self, scope, tableid):
		""""""
		base_query = "c.scope, a.name, c.adapter, c.enclosure, c.slot, c.raidlevel, c.arrayid, c.options from " \
		             "storage_controller as c inner join %s as a on c.tableid=%s where c.scope='%s'"
		order_by =  " order by enclosure, adapter, slot"
		needs_id = " and tableid = %s "

		querys = {'global' : "scope, adapter, enclosure, slot, raidlevel, arrayid, options from storage_controller "
		                     "where scope = 'global'" + order_by,
		          'os' : base_query % ('oses', 'a.id', 'os') + needs_id + order_by,
		          'appliance' : base_query % ('appliances', 'a.id', 'appliance') + needs_id + order_by,
		          'environment' : base_query % ('environments', 'a.id', 'environment') + needs_id + order_by,
		          'host' : base_query % ('nodes', 'a.id', 'host') + needs_id + order_by}

		if scope != 'global':
			return self.db.select(querys[scope], str(tableid))
		else:
			return self.db.select(querys[scope])



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
			fetchall = self.scope_query(scope, each_tableid)
			i = 0
			for row in fetchall:
				name = ''
				if scope == 'global':
					sql_scope, adapter, enclosure, slot, raidlevel, arrayid, options = row
				else:
					sql_scope, name, adapter, enclosure, slot, raidlevel, arrayid, options = row
				if adapter == -1:
					adapter = None
				if enclosure == -1:
					enclosure = None
				if slot == -1:
					slot = '*'
				if raidlevel == '-1':
					raidlevel = 'hotspare'
				if arrayid == -1:
					arrayid = 'global'
				elif arrayid == -2:
					arrayid = '*'
				# Remove leading and trailing double quotes
				options = options.strip("\"")

				if scope == 'global':
					self.addOutput(sql_scope, [enclosure, adapter, slot, raidlevel, arrayid, options])
				else:
					self.addOutput(sql_scope, [name, enclosure, adapter, slot, raidlevel, arrayid, options])

				i += 1

		if scope == 'global':
			self.endOutput(header=['scope', 'enclosure', 'adapter', 'slot',
			                       'raidlevel', 'arrayid', 'options'], trimOwner=False)
		else:

			self.endOutput(header=['scope', 'name', 'enclosure', 'adapter', 'slot',
			                       'raidlevel', 'arrayid', 'options'], trimOwner=False)