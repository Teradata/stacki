from stack.exception import CommandError
from collections import defaultdict

class VmArgumentProcessor():
	"""
	Mixin class to collect various functions for getting
	virtual machine values
	"""

	def vm_by_name(self, vm_name):
		"""
		Return a virtual machine's info
		by its hostname. All required info must be
		present for a return value to be present
		(hypervisor id, host id, memory, and cpu )
		"""

		result = self.db.select(
			"""
			* FROM virtual_machines vm
			INNER JOIN nodes ON vm.node_id = nodes.id
			WHERE nodes.name = %s AND COALESCE(vm.id, vm.hypervisor_id, vm.node_id, vm.memory_size, vm.cpu_cores)
			IS NOT NULL
			""", (vm_name)
		)
		return result

	def vm_id_by_name(self, vm_name):
		"""
		Get the id in the virtual machine's table
		by the vm hostname
		"""

		result = self.db.select(
			"""
			virtual_machines.id FROM virtual_machines
			INNER JOIN nodes ON virtual_machines.node_id = nodes.id
			WHERE nodes.name = %s
			""", (vm_name)
		)
		if result:
			return result[0][0]

	def valid_vm(self, vm_name):
		"""
		Determine if the given input host is a valid virtual machine
		"""

		# If vm_by_name returns a non empty value for the given input,
		# it is a valid input as all required values are present in the
		# database table
		if not self.vm_by_name(vm_name):
			return False
		else:
			return True

	def valid_vm_args(self, args):
		"""
		Returns a list of valid virtual machines to the caller
		Raises a CommandError if one or more hosts are not
		valid virtual machines
		"""

		hosts = self.getHostnames(args)

		# Use valid_vm to determine if the vm is
		# defined
		vm_hosts = self.getHostnames(args,
			host_filter = lambda self, host: self.valid_vm(host)
		)
		vm_hosts = list(vm_hosts)

		# Need to check if args is empty or not
		# as getHostnames will return all hosts if args
		# is empty and in that case we skip the check
		if args and vm_hosts != hosts:
			raise CommandError(self, f'One or more hosts are not a valid virtual machine')
		return vm_hosts

	def get_hypervisor_by_name(self, vm_name):
		"""
		Get the hostname of a vm's hypervisor via
		the vm hostname
		"""

		vm_id = self.vm_id_by_name(vm_name)
		result = self.db.select(
			"""
			nodes.name FROM nodes INNER JOIN virtual_machines
			ON nodes.id = virtual_machines.hypervisor_id AND
			virtual_machines.id = %s
			""", (vm_id, )
		)
		if result:
			return result[0][0]

	def is_hypervisor(self, hypervisor):
		"""
		Determine if the input host is a valid hypervisor
		via it's appliance.
		"""

		appliance = self.getHostAttr(hypervisor, 'appliance')
		if appliance == 'vms' or appliance == 'hypervisor':
			return True
		else:
			return False

	def hypervisor_id_by_name(self, hypervisor):
		"""
		Get the hypervisor id in the nodes table via
		its hostname
		"""

		return self.db.select(
			"""
			nodes.id FROM nodes WHERE nodes.name = %s
			""", (hypervisor, )
		)

	def vm_info(self, hosts):
		"""
		Get virtual specific attributes
		from the database and return it
		with the hostnames as keys
		"""

		vm_info = defaultdict(list)

		# Copy the hosts arg to append extra
		# parameters
		for row in self.db.select(
			"""
			nodes.name, (SELECT name FROM nodes WHERE nodes.id = vm.hypervisor_id)
			AS hypervisor, vm.memory_size, vm.cpu_cores, vm.vm_delete FROM nodes INNER JOIN virtual_machines vm
			ON nodes.id = vm.node_id
			"""):
			if row[0] in hosts:
				vm_info[row[0]].extend(row[1:-1])

				# Turn the integer value stored in the database to a
				# boolean for display
				vm_info[row[0]].append(bool(row[-1]))

		return vm_info

	def get_all_disks(self, hosts):
		"""
		Return a dict of vm disk info ordered by hostname
		"""

		disks = defaultdict(dict)
		for row in self.db.select(
			"""
			nodes.name, vmd.id, disk_name, disk_type, disk_location, disk_size, image_file_name, image_archive_name,
			mount_disk, vmd.disk_delete FROM virtual_machine_disks vmd INNER JOIN virtual_machines vm
			ON vmd.virtual_machine_id = vm.id INNER JOIN nodes ON vm.node_id = nodes.id
			"""):
				if row[0] in hosts:
					disks[row[0]][row[1]] = list(row[2:-1])

					# Turn disk deletion value into a bool
					# for display
					disks[row[0]][row[1]].append(bool(row[-1]))
		return disks

	def delete_pending_disk(self, host, disk_name):
		"""
		For a given host and disk name, delete it
		from the database if it's been marked for
		deletion prior via remove vm storage command
		"""

		vm_id = self.vm_id_by_name(host)
		return self.db.execute(
			"""
			DELETE FROM virtual_machine_disks WHERE
			virtual_machine_disks.virtual_machine_id = %s AND
			virtual_machine_disks.disk_delete = 1 AND
			virtual_machine_disks.disk_name = %s
			""", (vm_id, disk_name)
		)

	def delete_pending_vm(self, host):
		"""
		For a given virtual machine,
		Delete it from the database if
		its been marked for deletion prior
		via remove vm command
		"""

		vm_id = self.vm_id_by_name(host)
		return self.db.execute(
			"""
			DELETE FROM virtual_machines WHERE
			virtual_machines.id = %s AND
			virtual_machines.vm_delete = 1
			""", (vm_id, )
		)
