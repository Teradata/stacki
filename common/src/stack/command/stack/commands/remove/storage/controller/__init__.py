# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@

import stack.commands
from stack.exception import ArgRequired, ArgValue, ParamType, ParamValue, ParamError


class Command(stack.commands.remove.command, stack.commands.ScopeParamProcessor):
	"""
	Remove a storage controller configuration from the database.

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

	<param type='int' name='adapter' optional='1'>
	Adapter address. If adapter is '*', enclosure/slot address applies to
	all adapters.
	</param>

	<param type='int' name='enclosure' optional='1'>
	Enclosure address. If enclosure is '*', adapter/slot address applies
	to all enclosures.
	</param>

	<param type='int' name='slot'>
	Slot address(es). This can be a comma-separated list. If slot is '*',
	adapter/enclosure address applies to all slots.
	</param>

	<example cmd='remove storage controller backend-0-0 slot=1 scope=host'>
	Remove the disk array configuration for slot 1 on the host 'backend-0-0'.
	</example>

	<example cmd='remove storage controller backend slot=1,2,3,4 scope=appliance'>
	Remove the disk array configuration for slots 1-4 for the appliance 'backend'.
	</example>
	"""

	def validation(self, adapter, enclosure, arrayid, slot):
		"""Validate the parameters input."""
		if adapter and adapter != '*':
			try:
				adapter = int(adapter)
			except:
				raise ParamType(self, 'adapter', 'integer')
			if adapter < 0:
				raise ParamValue(self, 'adapter', '>= 0')
		else:
			adapter = -1

		if enclosure and enclosure != '*':
			try:
				enclosure = int(enclosure)
			except:
				raise ParamType(self, 'enclosure', 'integer')
			if enclosure < 0:
				raise ParamValue(self, 'enclosure', '>= 0')
		else:
			enclosure = -1

		if arrayid and arrayid != '*':
			try:
				arrayid = int(arrayid)
			except:
				raise ParamType(self, 'enclosure', 'integer')
			if arrayid < 0:
				raise ParamValue(self, 'enclosure', '>= 0')
		else:
			arrayid = -1

		slots = []
		if slot and slot != '*':
			for s in slot.split(','):
				try:
					s = int(s)
				except:
					raise ParamType(self, 'slot', 'integer')
				if s < 0:
					raise ParamValue(self, 'slot', '>= 0')
				if s in slots:
					raise ParamError(self, 'slot', '"%s" is listed twice' % s)
				slots.append(s)
		return adapter, enclosure, arrayid, slots


	def run(self, params, args):
		scope, adapter, enclosure, arrayid, slot = self.fillParams([
			('scope', 'global'),
			('adapter', '*'),
			('enclosure', None),
			('arrayid', None),
			('slot', None, True)
			])
		adapter, enclosure, arrayid, slots = self.validation(adapter, enclosure, arrayid, slot)
		# look up the id in the appropriate 'scope' table
		tableids = self.get_scope_name_tableid(scope, params, args)
		for each_tableid in tableids:

			deletesql = "delete from storage_controller where scope = %s and tableid = %s "
			delete_tuple = (scope, each_tableid)

			if adapter and adapter != '*' and adapter != -1:
				deletesql += " and adapter = %s"
				delete_tuple += (adapter,)

			if enclosure and enclosure != '*' and enclosure != -1:
				deletesql += " and enclosure = %s"
				delete_tuple += (enclosure,)

			if arrayid and arrayid != '*' and arrayid != -1:
				deletesql += " and arrayid = %s"
				delete_tuple += (arrayid,)

			if slot and slot != '*':
				for slot in slots:
					deletesql += " and slot = %s"
					delete_tuple += (slot,)

			self.db.execute(deletesql, delete_tuple)
