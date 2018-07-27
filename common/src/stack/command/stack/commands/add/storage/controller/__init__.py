# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@

import stack.commands
from stack.exception import CommandError, ParamRequired, ParamType, ParamValue, ParamError

class Command(stack.commands.add.command, stack.commands.ScopeParamProcessor):
	"""
	Add a storage controller configuration to the database.

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
	Adapter address.
	</param>

	<param type='int' name='enclosure' optional='1'>
	Enclosure address.
	</param>

	<param type='int' name='slot'>
	Slot address(es). This can be a comma-separated list meaning all disks
	in the specified slots will be associated with the same array
	</param>

	<param type='int' name='raidlevel'>
	RAID level. Raid 0, 1, 5, 6 and 10 are currently supported.
	</param>

	<param type='int' name='hotspare' optional='1'>
	Slot address(es) of the hotspares associated with this array id. This
	can be a comma-separated list (like the 'slot' parameter). If the
	'arrayid' is 'global', then the specified slots are global hotspares.
	</param>

	<param type='string' name='arrayid'>
	The 'arrayid' is used to determine which disks are grouped as part
	of the same array. For example, all the disks with arrayid of '1' will
	be part of the same array. Arrayids must be integers starting at 1
	or greater. If the arrayid is 'global', then 'hotspare' must
	have at least one slot definition (this is how one specifies a global
	hotspare).
	In addition, the arrays will be created in arrayid order, that is,
	the array with arrayid equal to 1 will be created first, arrayid
	equal to 2 will be created second, etc.
	</param>

	<example cmd='add storage controller backend-0-0 slot=1 raidlevel=0 arrayid=1 scope=host'>
	The disk in slot 1 on backend-0-0 should be a RAID 0 disk, for the host 'backend-0-0'
	</example>

	<example cmd='add storage controller backend-0-0 slot=2,3,4,5,6 raidlevel=6 hotspare=7,8 arrayid=2 scope=host'>
	The disks in slots 2-6 on backend-0-0 should be a RAID 6 with two
	hotspares associated with the array in slots 7 and 8, for the host 'backend-0-0'
	</example>
	"""

	def check_for_duplicates(self, scope, tableid, enclosure, slot):
		# Intentionally not looking for adapter, as regardless of the adapter a disk can't be used twice
		row = self.db.select("""scope, tableid, adapter, enclosure, slot from storage_controller 
			where scope = '%s' and tableid = %s and enclosure = %s and slot = %s""" %
		                (scope, tableid, enclosure, slot))

		if row:
			if scope == 'host':
				# Give useful error with host name instead of just generic 'host'
				scope = self.db.select('name from nodes where id = %s', str(tableid))[0][0]
			raise CommandError(self, 'controller specification for enclosure "%s", slot "%s" already '
			                         'exists in the database for scope: "%s"'  % (enclosure, slot, scope))


	def validation(self, adapter, enclosure, slot, hotspare, raidlevel, arrayid):
		"""
		Validate the data input matches the requirements to be usable.
		Also I wanted to be able to call self.validation
		"""
		if not hotspare and not slot:
			raise ParamRequired(self, ['slot', 'hotspare'])
		if arrayid != 'global' and not raidlevel:
			raise ParamRequired(self, 'raidlevel')

		if adapter:
			try:
				adapter = int(adapter)
			except:
				raise ParamType(self, 'adapter', 'integer')
			if adapter < 0:
				raise ParamValue(self, 'adapter', '>= 0')
		else:
			adapter = -1

		if enclosure:
			try:
				enclosure = int(enclosure)
			except:
				raise ParamType(self, 'enclosure', 'integer')
			if enclosure < 0:
				raise ParamValue(self, 'enclosure', '>= 0')
		else:
			enclosure = -1

		slots = []
		if slot:
			for s in slot.split(','):
				if s == '*':
					# represent '*' in the database as '-1'
					s = -1
				else:
					try:
						s = int(s)
					except:
						raise ParamType(self, 'slot', 'integer')
					if s < 0:
						raise ParamValue(self, 'slot', '>= 0')
					if s in slots:
						raise ParamError(self, 'slot', ' "%s" is listed twice' % s)
				slots.append(s)

		hotspares = []
		if hotspare:
			for h in hotspare.split(','):
				try:
					h = int(h)
				except:
					raise ParamType(self, 'hotspare', 'integer')
				if h < 0:
					raise ParamValue(self, 'hostspare', '>= 0')
				if h in hotspares:
					raise ParamError(self, 'hostspare', ' "%s" is listed twice' % h)
				hotspares.append(h)

		if arrayid in [ 'global', '*' ]:
			pass
		else:
			try:
				arrayid = int(arrayid)
			except:
				raise ParamType(self, 'arrayid', 'integer')
			if arrayid < 1:
				raise ParamValue(self, 'arrayid', '>= 0')

		if arrayid == 'global' and len(hotspares) == 0:
			raise ParamError(self, 'arrayid', 'is "global" with no hotspares. Please supply at least one hotspare')

		# Some may have been modified to be -1/*, turned into a list, etc.
		return adapter, enclosure, slots, hotspares, arrayid


	def run(self, params, args):

		scope, adapter, enclosure, slot, hotspare, raidlevel, arrayid, options, force = self.fillParams([
			('scope', 'global'),
			('adapter', None),
			('enclosure', None),
			('slot', None),
			('hotspare', None),
			('raidlevel', None),
			('arrayid', None, True),
			('options', ''),
			('force', 'n')
			])

		tableids = self.get_scope_name_tableid(scope, params, args)
		# make sure the specification doesn't already exist
		adapter, enclosure, slots, hotspares, arrayid = self.validation(adapter, enclosure, slot, hotspare,
		                                                                raidlevel, arrayid)

		force = self.str2bool(force)
		for tableid in tableids:
			for slot in slots:
				if not force:
					self.check_for_duplicates(scope, tableid, enclosure, slot)
			for hotspare in hotspares:
				if not force:
					self.check_for_duplicates(scope, tableid, enclosure, hotspare)

			if arrayid == 'global':
				arrayid = -1
			elif arrayid == '*':
				arrayid = -2

			# now add the specifications to the database
			for slot in slots:
				self.db.execute("""insert into storage_controller
					(scope, tableid, adapter, enclosure, slot,
					raidlevel, arrayid, options) values (%s, %s, %s, %s,
					%s, %s, %s, %s) """, (scope, tableid, adapter,
					enclosure, slot, raidlevel, arrayid, options))

			for hotspare in hotspares:
				raidlevel = -1
				if arrayid == 'global':
					arrayid = -1

				self.db.execute("""insert into storage_controller
					(scope, tableid, adapter, enclosure, slot,
					raidlevel, arrayid, options) values (%s, %s, %s, %s,
					%s, %s, %s, %s) """, (scope, tableid, adapter,
					enclosure, hotspare, raidlevel, arrayid, options))
