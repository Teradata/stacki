# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
from collections import defaultdict
from collections import OrderedDict
from pathlib import Path
import json


class Command(stack.commands.dump.command):
	"""
	Dump the contents of the stacki database as json.

	This command dumps specifically the virtual machine data.
	For each host added as a virtual machine, it will dump the
	vm specific data including the hypervisor, storage, memory,
	and cpu cores

	<example cmd='dump vm'>
	Dump json data for virtual machines in the stacki database
	</example>

	<related>load</related>
	"""

	def run(self, params, args):

		# Get all our storage info first
		# so the command only has to be run
		# once for all VM hosts
		storage = defaultdict(list)
		for row in self.call('list.vm.storage'):
			host = row['Virtual Machine']
			disk_loc = Path(row['Location']).parent
			storage[host].append(OrderedDict(
				disk_name  = row['Name'],
				disk_type  = row['Type'],
				location   = str(disk_loc),
				size       = row['Size'],
				image_name = row['Image Name'],
				mountpoint = row['Mountpoint']))

		dump = []

		# Dump our VM host information
		for row in self.call('list.vm', args):
			name = row['virtual machine']
			dump.append(OrderedDict(
				name       = name,
				hypervisor = row['hypervisor'],
				memory     = row['memory'],
				cpu        = row['cpu'],
				disks      = storage[name]))

		self.addText(json.dumps(OrderedDict(vm=dump), indent=8))
