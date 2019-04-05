# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError, ParamRequired, ParamType, ParamValue


class Command(stack.commands.ScopeArgumentProcessor, stack.commands.add.command):
	"""
	Add a global storage partition configuration for the all hosts in the cluster.

	<param type='string' name='device' optional='0'>
	Disk device on which we are creating partitions
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint to create
	</param>

	<param type='integer' name='size' optional='0'>
	Size of the partition.
	</param>

	<param type='string' name='type' optional='1'>
	Type of partition E.g: ext4, ext3, xfs, raid, etc.
	</param>

	<param type='string' name='options' optional='1'>
	Options that need to be supplied while adding partitions.
	</param>

	<param type='integer' name='partid' optional='1'>
	The relative partition id for this partition. Partitions will be
	created in ascending partition id order.
	</param>

	<example cmd='add storage partition device=sda mountpoint=/var size=50 type=ext4'>
	Creates a ext4 partition on device sda with mountpoints /var.
	</example>

	<example cmd='add storage partition device=sdc mountpoint=pv.01 size=0 type=lvm'>
	Creates a physical volume named pv.01 for lvm.
	</example>

	<example cmd='add storage partition device=volgrp01 mountpoint=/banktools size=8192 type=xfs options=--name=banktools'>
	Created an xfs lvm partition of size 8192 on volgrp01. volgrp01 needs to be created
	with the previous example.
	</example>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		device, size, fstype, mountpoint, options, partid = self.fillParams([
			('device', None, True),
			('size', None, True),
			('type', None),
			('mountpoint', None),
			('options', None),
			('partid', None),
		])

		if not device:
			raise ParamRequired(self, 'device')

		if not size:
			raise ParamRequired(self, 'size')

		# Validate size
		if mountpoint == 'swap' and size in ['recommended', 'hibernation']:
			if size == 'recommended':
				size = -1
			else:
				size = -2
		else:
			try:
				size = int(size)
			except:
				raise ParamType(self, 'size', 'integer')

			if size < 0:
				raise ParamValue(self, 'size', '>= 0')

		# Validate partid
		if partid:
			try:
				partid = int(partid)
			except ValueError:
				raise ParamType(self, 'partid', 'integer')

			if partid < 1:
				raise ParamValue(self, 'partid', '>= 0')
		else:
			partid = 0

		# Make sure the specification for mountpoint doesn't already exist
		if mountpoint:
			# Needs to be unique in the scope
			for scope_mapping in scope_mappings:
				# Check that the route is unique for the scope
				if self.db.count("""
					(storage_partition.id)
					FROM storage_partition,scope_map
					WHERE storage_partition.scope_map_id = scope_map.id
					AND storage_partition.device = %s
					AND storage_partition.mountpoint = %s
					AND scope_map.scope = %s
					AND scope_map.appliance_id <=> %s
					AND scope_map.os_id <=> %s
					AND scope_map.environment_id <=> %s
					AND scope_map.node_id <=> %s
				""", (device, mountpoint, *scope_mapping)) != 0:
					raise CommandError(
						self,
						f'partition specification for device "{device}" '
						f'and mount point "{mountpoint}" already exists'
					)
		else:
			mountpoint = None

		if not fstype:
			fstype = None

		if not options:
			options = ""

		# Everything is valid, add the data for each scope_mapping
		for scope_mapping in scope_mappings:
			# First add the scope mapping
			self.db.execute("""
				INSERT INTO scope_map(
					scope, appliance_id, os_id, environment_id, node_id
				)
				VALUES (%s, %s, %s, %s, %s)
			""", scope_mapping)

			# Then add the storage partition entry
			self.db.execute("""
				INSERT INTO storage_partition(
					scope_map_id, device, mountpoint,
					size, fstype, options, partid
				)
				VALUES (LAST_INSERT_ID(), %s, %s, %s, %s, %s, %s)
			""", (device, mountpoint, size, fstype, options, partid))
