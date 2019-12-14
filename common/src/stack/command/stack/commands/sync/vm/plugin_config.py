# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.kvm import Hypervisor
from stack.kvm import VmException
from stack.util import _exec

class Plugin(stack.commands.Plugin):
	"""
	Plugin that syncs the database
	values with the current state
	of each virtual machine and
	its storage
	"""

	def provides(self):
		return 'config'

	# Run plugins that handle the non
	# configuration work first
	def requires(self):
		return ['hypervisor', 'storage']

	def run(self, args):
		vm_hosts, host_disks, debug, sync_ssh, force, autostart = args
		config_errors = []
		self.owner.notify('Sync VM Config')

		# Check if the each disk that has been marked
		# for deletion is no longer on the hypervisor
		# then delete it from the database
		for host, disks in host_disks.items():
			for disk in disks:
				delete_disk = self.owner.str2bool(disk['Pending Deletion'])
				hypervisor = vm_hosts[host]['hypervisor']
				disk_name = disk['Name']

				# Just remove mounted storage as there
				# isn't any files to delete
				if disk['Type'] == 'mountpoint':
					if delete_disk:
						self.owner.delete_pending_disk(host, disk_name)
					continue
				disk_loc = f'{disk["Location"]}/{disk["Image Name"]}'

				# ls has a nonzero returncode if the file isn't found
				# meaning it can be deleted from the database
				disk_on_hypervisor = _exec(f'ssh {hypervisor} "ls {disk_loc}"', shlexsplit=True)
				if delete_disk and (force or disk_on_hypervisor.returncode != 0):
					self.owner.delete_pending_disk(host, disk_name)

		# Start any virtual machines that have been defined
		# if the autostart parameter isn't set to False
		for host in self.owner.call('list.vm', [*vm_hosts, 'expanded=True']):
			hostname = host['virtual machine']
			delete_vm = self.owner.str2bool(host['pending deletion'])
			hypervisor_host = host['hypervisor']
			status = host['status']
			if status == 'off':
				try:
					conn = Hypervisor(hypervisor_host)
					if autostart:
						self.owner.notify(f'Starting {hostname} on {hypervisor_host}')
						conn.start_domain(hostname)

					# Always set the vm to start on boot
					# of hypervisor
					conn.autostart(hostname, True)
				except VmException as error:
					config_errors.append(f'Could not start VM {hostname}:\n{str(error)}')

			# Remove any virtual machines pending for deletion
			# from the database if the status can be retrieved
			# or the force parameter was set
			if (force or (status in ['undefined', 'off'])) and delete_vm:
				self.owner.delete_pending_vm(hostname)
				self.owner.notify(f'Removing VM {hostname}')

		return config_errors
