# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError, ParamRequired, ParamType, ParamValue


class Command(stack.commands.add.command, stack.commands.ScopeParamProcessor):
	"""
	Add a partition configuration to the database.

	<arg optional='1' type='string' name='host'>
	This argument can be nothing, a valid 'os' (e.g., 'redhat'), a valid
	appliance (e.g., 'backend') or a host.
	If nothing is supplied, then the global storage partition
	configuration will be output.
	</arg>

	<param type='string' name='scope'>
	Zero or one parameter. The parameter is the scope for the provided name
	(e.g., 'os', 'host', 'environment', 'appliance').
	No scope means the scope is 'global', and no name will be accepted.
	</param>

	<param type='string' name='device' optional='0'>
	Disk device on which we are creating partitions
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint to create
	</param>

	<param type='int' name='size' optional='0'>
	Size of the partition.
	</param>

	<param type='string' name='type' optional='1'>
	Type of partition E.g: ext4, ext3, xfs, raid, etc.
	</param>

	<param type='string' name='options' optional='0'>
	Options that need to be supplied while adding partitions.
	</param>

	<param type='int' name='partid' optional='1'>
	The relative partition id for this partition. Partitions will be
	created in ascending partition id order.
	</param>

	<example cmd='add storage partition backend-0-0 device=sda mountpoint=/var
		size=50 type=ext4'>
	Creates a ext4 partition on device sda with mountpoints /var.
	</example>

	<example cmd='add storage partition backend-0-2 device=sdc mountpoint=pv.01
		 size=0 type=lvm'>
	Creates a physical volume named pv.01 for lvm.
	</example>

	<example cmd='add storage partition backend-0-2 mountpoint=volgrp01 device=pv.01 pv.02 pv.03
		size=32768 type=volgroup'>
	Creates a volume group from 3 physical volumes i.e. pv.01, pv.02, pv.03. All these 3
	physical volumes need to be created with the previous example. PV's need to be space
	separated.
	</example>
	<example cmd='add storage partition backend-0-2 device=volgrp01 mountpoint=/banktools
		size=8192 type=xfs options=--name=banktools'>
	Created an xfs lvm partition of size 8192 on volgrp01. volgrp01 needs to be created
	with the previous example.
	</example>
	"""

	#
	def check_mount_point(self, device, scope, tableid, mountpt):
		""" Checks if partition config already exists in DB for a device and a mount point."""
		if mountpt:
			self.db.execute("""select Scope, TableID, Mountpoint,
				device, Size, FsType from storage_partition where
				Scope=%s and TableID=%s and device= %s
				and Mountpoint=%s""", (scope, tableid, device, mountpt))
			row = self.db.fetchone()
			if row:
				if scope == 'host':
					# Give useful error with host name instead of just generic 'host'
					scope = self.db.select('name from nodes where id = %s', str(tableid))[0][0]
				raise CommandError(self, 'partition specification for device "%s", mount point "%s" already exists in the '
				                         'database for scope: "%s"' % (device, mountpt, scope))
		return

	def check_dev_and_partid(self, device, scope, tableid, partid):
		""" Checks if partition config already exists in DB for a device and a partid."""
		self.db.execute("""select Scope, TableID, PartID,
			device, Size, FsType from storage_partition where
			Scope=%s and TableID=%s and device= %s
			and partid=%s""", (scope, tableid, device, partid))
		row = self.db.fetchone()
		if row:
			if scope == 'host':
					# Give useful error with host name instead of just generic 'host'
				scope = self.db.select('name from nodes where id = %s', str(tableid))[0][0]
			raise CommandError(self, 'partition specification for device "%s", partition id "%s" already exists in '
			                         'the database for scope: "%s"' % (device, partid, scope))

	def check_for_duplicates(self, device, scope, tableid, mountpt, partid):

		self.db.execute("""select Scope, TableID, Mountpoint,
			device, Size, FsType from storage_partition where
			Scope=%s and TableID=%s and device= %s
			and Mountpoint=%s and partid=%s""", (scope, tableid, device, mountpt, partid))
		row = self.db.fetchone()
		if row:
			if scope == 'host':
				# Give useful error with host name instead of just generic 'host'
				scope = self.db.select('name from nodes where id = %s', str(tableid))[0][0]
			raise CommandError(self, 'partition specification for device "%s", mount point "%s" already exists in the '
			                         'database for scope: "%s"' % (device, mountpt, scope))

		self.check_mount_point(device, scope, tableid, mountpt)
		if partid:
			self.check_dev_and_partid(device, scope, tableid, partid)

	def validation(self, size, mountpt, partid):
		"""Validate size and partid that were input."""
		if size:
			try:
				s = int(size)
			except (ValueError, TypeError):
				#
				# If mountpoint is 'swap' then allow
				# 'hibernate', 'recommended' as sizes.
				#
				if mountpt == 'swap' and size not in ['recommended', 'hibernation']:
						raise ParamType(self, 'size', 'integer')
				else:
					raise ParamType(self, 'size', 'integer')
			if s < 0:
				raise ParamValue(self, 'size', '>= 0')

		# Validate partid
		if partid:
			try:
				p = int(partid)
			except ValueError:
				raise ParamValue(self, 'partid', 'an integer')

			if p < 1:
				raise ParamValue(self, 'partid', '>= 0')

			partid = p
		return partid

	def run(self, params, args):
		scope, device, size, fstype, mountpt, options, partid = self.fillParams([
			('scope', 'global'),
			('device', None, True),
			('size', None),
			('type', None),
			('mountpoint', None),
			('options', None),
			('partid', None), ])

		if not device:
			raise ParamRequired(self, 'device')
		# If size is blank then the sql command will crash
		if not size:
			raise ParamRequired(self, 'size')

		self.validation(size, mountpt, partid)
		# Also clean up the Nones to empty strings or 0.
		if not options:
			options = ''
		if not fstype:
			fstype = ''
		if not mountpt:
			mountpt = ''
		# Not certain this won't break something down the line. Load storage partition auto determines this...
		if not partid:
			partid = 0

		tableids = self.get_scope_name_tableid(scope, params, args)
		# if we get a:backend we want to check that all will go through instead of doing some then failing:
		for each_tableid in tableids:
			# make sure the specification for mountpt doesn't already exist
			self.check_for_duplicates(device, scope, each_tableid, mountpt, partid)


		for each_tableid in tableids:
			# now add the specifications to the database
			sql_statement = "(Scope, TableID, device, Mountpoint,  Size, FsType, Options , PartID) values (%s, %s, " \
			                "%s,  %s, %s, %s, %s, %s)"
			sql_vars = (scope, each_tableid, device, mountpt, size, fstype, options, partid)

			self.db.execute("insert into storage_partition " + sql_statement, sql_vars)
