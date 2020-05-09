# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from pathlib import Path

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'vm'

	def requires(self):
		return [ 'host' ]

	def run(self, section):

		# Add virtual machine hosts
		for vm in section:
			host  = vm.get('name', '')
			params = {
				'hypervisor' : vm.get('hypervisor', ''),
				'memory'     : vm.get('memory', ''),
				'cpu'        : vm.get('cpu', '')
			}

			self.owner.stack('add.vm', host, **params)

			# Add virtual machine storage
			for disk in vm.get('disks', []):
				disk_type = disk.get('disk_type', '')
				add_disk = ''

				# add vm storage requires different input
				# for the disks parameter depending on the disk type
				# 1. Pre-made disk files use the file path to the image
				#    on the frontend
				# 2. New disks created by the hypervisor are just the size of the disk
				# 3. Mountpoints are just the physical disk path on the hypervisor
				if disk_type == 'image':
					add_disk = disk.get('image_name', '')
				elif disk_type == 'disk':
					add_disk = disk.get('size', '')
				elif disk_type == 'mountpoint':
					add_disk = disk.get('mountpoint', '')

				add_params = {
					'storage_pool': disk.get('location' ''),
					'name'        : disk.get('disk_name', ''),
					'disks'       : add_disk
				}
				self.owner.stack('add.vm.storage', host, **add_params)
