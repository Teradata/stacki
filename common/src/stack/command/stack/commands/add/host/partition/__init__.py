#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands


class Command(stack.commands.add.host.command):
	"""
	Add Partitioning information to the database.
	
	<arg name="host" type="string" repeat="1">
	Hostname
	</arg>

	<param name="device"  type="string">
	Device to be added. For example, sdb, sdb1, etc.
	</param>

	<param name="mountpoint" type="string">
	Mount point for the device. For example, "/state/partition1", "/hadoop01".
	</param>

	<param name="uuid" type="string">
	UUID for the partition
	</param>

	<param name="sectorstart" type="string">
	Starting sector of partition
	</param>

	<param name="size" type="string">
	Size of partition
	</param>

	<param name="partid" type="string">
	ID of partition
	</param>

	<param name="fs" type="string">
	File system type of partition. For example, "ext4", "xfs"
	</param>

	<param name="partitionflags" type="string">
	Flags used for partitioning
	</param>

	<param name="formatflags" type="string">
	Flags used for formatting the partition
	</param>
	"""

	def run(self, params, args):
		hosts = self._get_hosts(args)
		
		(device, mountpoint, uuid, sectorstart, size, partitionid,
		fs, partitionflags, formatflags) = self.fillParams([
			("device", None, True),
			("mountpoint", ""),
			("uuid", ""),
			("sectorstart", 0),
			("size", 0),
			("partid", ""),
			("fs", ""),
			("partitionflags", ""),
			("formatflags", ""),
		])

		for host in hosts:
			# If we already have partition info, remove it for this host
			if self.db.select("""count(p.ID) from partitions p, nodes n
				where p.node=n.id and n.name=%s and p.device=%s""",
				(host, device)
			)[0][0] != 0:
				self.command("remove.host.partition", (host, f"device={device}"))
			
			# Insert the new partition info
			self.db.execute("""
				insert into partitions(
					node, device, mountpoint, uuid, sectorstart, PartitionSize,
					PartitionID, FsType, PartitionFlags, FormatFlags
				) values (
					(select id from nodes where name=%s),
					%s, %s, %s, %s, %s, %s, %s, %s, %s
				)""", (
					host, device, mountpoint, uuid, sectorstart, size,
					partitionid, fs, partitionflags, formatflags
				))
