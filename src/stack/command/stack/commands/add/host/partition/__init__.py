#
# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#

import os
import sys
import stack.commands
from stack.exception import *

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
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
		hosts = self.getHostnames(args)
		
		(device, mountpoint, uuid,
		sectorstart, size, partitionid,
		fs, partitionflags, formatflags) = self.fillParams([
				("device", None, True),
				("mountpoint",""),
				("uuid",""),
				("sectorstart", 0),
				("size", 0),
				("partid", ""),
				("fs", ""),
				("partitionflags",""),
				("formatflags", ""),
			])

		for host in hosts:
			sql_cmd = """select p.id from partitions p, nodes n
				where p.node=n.id and n.name="%s" and
				p.device="%s" """ % (host, device)
			self.db.execute(sql_cmd)
			r = self.db.fetchall()
			if r > 0:
				self.command("remove.host.partition",
					[host, "device=%s" % device])
			sql_cmd = """insert into partitions
				(node, device, mountpoint, uuid, sectorstart,
				PartitionSize, PartitionID, FsType,
				PartitionFlags, FormatFlags) values
				((select id from nodes where name="%s"),
				'%s','%s','%s','%s','%s','%s','%s','%s','%s')""" \
				% (host, device, mountpoint, uuid, sectorstart,
				size, partitionid, fs, partitionflags, formatflags)
			self.db.execute(sql_cmd)
