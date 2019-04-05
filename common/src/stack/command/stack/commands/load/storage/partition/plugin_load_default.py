# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError


class Plugin(
	stack.commands.OSArgumentProcessor,
	stack.commands.ApplianceArgumentProcessor,
	stack.commands.Plugin
):
	"""
	Plugin that invokes 'stack add storage partition' and adds
	the partitions to the database.
	"""

	def provides(self):
		return 'default'

	def run(self, args):
		appliances = self.getApplianceNames()
		oses = self.getOSNames()

		for target, data in args.items():
			# Remove all existing entries
			cmdargs = []

			if target != 'global':
				cmdargs.append(target)

			cmdargs.append('device=*')

			try:
				if target == 'global':
					self.owner.call('remove.storage.partition', cmdargs)
				elif target in appliances:
					self.owner.call('remove.appliance.storage.partition', cmdargs)
				elif target in oses:
					self.owner.call('remove.os.storage.partition', cmdargs)
				else:
					self.owner.call('remove.host.storage.partition', cmdargs)
			except CommandError:
				# Nothing existed to remove
				pass

			# Loop through the devices in sorted order
			for device in sorted(data.keys()):
				for partition in data[device]:
					cmdargs = []
					if target != 'global':
						cmdargs.append(target)

					cmdargs.append(f'device={device}')

					if partition['mountpoint']:
						cmdargs.append(f"mountpoint={partition['mountpoint']}")

					if partition['type']:
						cmdargs.append(f"type={partition['type']}")

					cmdargs.append(f"size={partition['size']}")

					if partition['options']:
						cmdargs.append(f"options={partition['options']}")

					if partition['partid']:
						cmdargs.append(f"partid={partition['partid']}")

					if target == 'global':
						self.owner.call('add.storage.partition', cmdargs)
					elif target in appliances:
						self.owner.call('add.appliance.storage.partition', cmdargs)
					elif target in oses:
						self.owner.call('add.os.storage.partition', cmdargs)
					else:
						self.owner.call('add.host.storage.partition', cmdargs)
