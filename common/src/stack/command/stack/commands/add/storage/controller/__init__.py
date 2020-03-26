# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import ScopeArgProcessor
from stack.exception import CommandError, ParamRequired, ParamType, ParamValue, ParamError


class Command(ScopeArgProcessor, stack.commands.add.command):
	"""
	Add a global storage controller configuration for the all hosts in the cluster.

	<param type='integer' name='adapter' optional='1'>
	Adapter address.
	</param>

	<param type='integer' name='enclosure' optional='1'>
	Enclosure address.
	</param>

	<param type='integer' name='slot'>
	Slot address(es). This can be a comma-separated list meaning all disks
	in the specified slots will be associated with the same array
	</param>

	<param type='integer' name='raidlevel'>
	RAID level. Raid 0, 1, 5, 6, 10, 50, 60 are currently supported.
	</param>

	<param type='integer' name='hotspare' optional='1'>
	Slot address(es) of the hotspares associated with this array id. This
	can be a comma-separated list (like the 'slot' parameter). If the
	'arrayid' is 'global', then the specified slots are global hotspares.
	</param>

	<param type='string' name='arrayid' optional='0'>
	The 'arrayid' is used to determine which disks are grouped as part
	of the same array. For example, all the disks with arrayid of '1' will
	be part of the same array.

	Arrayids must be integers starting at 1 or greater. If the arrayid is
	'global', then 'hotspare' must have at least one slot definition (this
	is how one specifies a global hotspare).

	In addition, the arrays will be created in arrayid order, that is,
	the array with arrayid equal to 1 will be created first, arrayid
	equal to 2 will be created second, etc.
	</param>

	<example cmd='add storage controller slot=1 raidlevel=0 arrayid=1'>
	The disk in slot 1 should be a RAID 0 disk.
	</example>

	<example cmd='add storage controller slot=2,3,4,5,6 raidlevel=6 hotspare=7,8 arrayid=2'>
	The disks in slots 2-6 should be a RAID 6 with two hotspares associated
	with the array in slots 7 and 8.
	</example>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		adapter, enclosure, slot, hotspare, raidlevel, arrayid, options = self.fillParams([
			('adapter', None),
			('enclosure', None),
			('slot', None),
			('hotspare', None),
			('raidlevel', None),
			('arrayid', None, True),
			('options', '')
		])

		# Gotta have either a hotspare list or a slot list
		if not hotspare and not slot:
			raise ParamRequired(self, ['slot', 'hotspare'])

		# Non-global arrays need a raid level
		if arrayid != 'global' and not raidlevel:
			raise ParamRequired(self, 'raidlevel')

		# Make sure the adapter is an integer greater than 0, if it exists
		if adapter:
			try:
				adapter = int(adapter)
			except:
				raise ParamType(self, 'adapter', 'integer')

			if adapter < 0:
				raise ParamValue(self, 'adapter', '>= 0')
		else:
			adapter = -1

		# Make sure the enclosure is an integer greater than 0, if it exists
		if enclosure:
			try:
				enclosure = int(enclosure)
			except:
				raise ParamType(self, 'enclosure', 'integer')

			if enclosure < 0:
				raise ParamValue(self, 'enclosure', '>= 0')
		else:
			enclosure = -1

		# Parse the slots
		slots = []
		if slot:
			for s in slot.split(','):
				# Make sure the slot is valid
				if s == '*':
					# Represent '*' in the database as '-1'
					s = -1
				else:
					try:
						s = int(s)
					except:
						raise ParamType(self, 'slot', 'integer')

					if s < 0:
						raise ParamValue(self, 'slot', '>= 0')

					if s in slots:
						raise ParamError(
							self, 'slot', f'"{s}" is listed twice'
						)

				# Needs to be unique in the scope
				for scope_mapping in scope_mappings:
					# Check that the route is unique for the scope
					if self.db.count("""
						(storage_controller.id)
						FROM storage_controller,scope_map
						WHERE storage_controller.scope_map_id = scope_map.id
						AND storage_controller.adapter = %s
						AND storage_controller.enclosure = %s
						AND storage_controller.slot = %s
						AND scope_map.scope = %s
						AND scope_map.appliance_id <=> %s
						AND scope_map.os_id <=> %s
						AND scope_map.environment_id <=> %s
						AND scope_map.node_id <=> %s
					""", (adapter, enclosure, s, *scope_mapping)) != 0:
		 				raise CommandError(
							self,
							f'disk specification for "{adapter}/'
							f'{enclosure}/{s}" already exists'
						)

				# Looks good
				slots.append(s)

		# Parse the hotspares
		hotspares = []
		if hotspare:
			for h in hotspare.split(','):
				# Make sure the hotspare is valid
				try:
					h = int(h)
				except:
					raise ParamType(self, 'hotspare', 'integer')

				if h < 0:
					raise ParamValue(self, 'hotspare', '>= 0')

				if h in hotspares:
					raise ParamError(
						self, 'hotspare', f'"{h}" is listed twice'
					)

				if h in slots:
					raise ParamError(
						self, 'hotspare', f'"{h}" is listed in slots'
					)

				# Needs to be unique in the scope
				for scope_mapping in scope_mappings:
					# Check that the route is unique for the scope
					if self.db.count("""
						(storage_controller.id)
						FROM storage_controller,scope_map
						WHERE storage_controller.scope_map_id = scope_map.id
						AND storage_controller.adapter = %s
						AND storage_controller.enclosure = %s
						AND storage_controller.slot = %s
						AND scope_map.scope = %s
						AND scope_map.appliance_id <=> %s
						AND scope_map.os_id <=> %s
						AND scope_map.environment_id <=> %s
						AND scope_map.node_id <=> %s
					""", (adapter, enclosure, h, *scope_mapping)) != 0:
		 				raise CommandError(
							self,
							f'disk specification for "{adapter}/'
							f'{enclosure}/{h}" already exists'
						)

				# Looks good
				hotspares.append(h)

		# Check the arrayid
		if arrayid not in {'global', '*'}:
			try:
				arrayid = int(arrayid)
			except:
				raise ParamType(self, 'arrayid', 'integer')

			if arrayid < 1:
				raise ParamValue(self, 'arrayid', '>= 1')

		if arrayid == 'global' and len(hotspares) == 0:
			raise ParamError(self, 'arrayid', 'is "global" with no hotspares')

		# Special encodings for arrayid
		if arrayid == 'global':
			arrayid = -1
		elif arrayid == '*':
			arrayid = -2

		# Everything is valid, add the data for each scope_mapping
		for scope_mapping in scope_mappings:
			# Add the slots
			for slot in slots:
				# First add the scope mapping
				self.db.execute("""
					INSERT INTO scope_map(
						scope, appliance_id, os_id, environment_id, node_id
					)
					VALUES (%s, %s, %s, %s, %s)
				""", scope_mapping)

				# Then add the slot controller entry
				self.db.execute("""
					INSERT INTO storage_controller(
						scope_map_id, adapter, enclosure, slot,
						raidlevel, arrayid, options
					)
					VALUES (LAST_INSERT_ID(), %s, %s, %s, %s, %s, %s)
				""", (adapter, enclosure, slot, raidlevel, arrayid, options))

			# And add the hotspares
			for hotspare in hotspares:
				# First add the scope mapping
				self.db.execute("""
					INSERT INTO scope_map(
						scope, appliance_id, os_id, environment_id, node_id
					)
					VALUES (%s, %s, %s, %s, %s)
				""", scope_mapping)

				# Then add the hotspare controller entry
				self.db.execute("""
					INSERT INTO storage_controller(
						scope_map_id, adapter, enclosure, slot,
						raidlevel, arrayid, options
					)
					VALUES (LAST_INSERT_ID(), %s, %s, %s, '-1', %s, %s)
				""", (adapter, enclosure, hotspare, arrayid, options))
