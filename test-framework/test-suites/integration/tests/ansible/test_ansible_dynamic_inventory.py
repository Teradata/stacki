import json

class TestAnsibleDynamicInventory:
	def test_selectors(self, host, host_os, add_host, add_group, test_file):
		"""
		Test that the plugin creates groups for all the selectors
		"""

		# Add the backend to the test group
		result = host.run('stack add host group backend-0-0 group=test')
		assert result.rc == 0

		# Get our inventory data
		result = host.run("ansible-inventory --list")
		assert result.rc == 0
		inventory = json.loads(result.stdout)

		# Remove the host vars section
		del inventory["_meta"]

		# See if all the groups are as expected
		with open(test_file(f'ansible/inventory_groups_{host_os}.json')) as output:
			assert inventory == json.loads(output.read())

	def test_attributes(self, host, add_host):
		"""
		Test that the plugin creates vars for host attributes
		"""

		# Add a unique attribute for the backend and the frontend
		result = host.run('stack add host attr frontend-0-0 attr=foo value=frontend')
		assert result.rc == 0

		result = host.run('stack add host attr backend-0-0 attr=bar value=backend')
		assert result.rc == 0

		# Get our inventory data
		result = host.run("ansible-inventory --list")
		assert result.rc == 0
		inventory = json.loads(result.stdout)

		# Check that intrinsic attributes exist
		assert inventory["_meta"]["hostvars"]["frontend-0-0"]["stacki_appliance"] == "frontend"
		assert inventory["_meta"]["hostvars"]["backend-0-0"]["stacki_appliance"] == "backend"

		# Make sure boolean strings are being converted
		assert inventory["_meta"]["hostvars"]["frontend-0-0"]["stacki_managed"] == False
		assert inventory["_meta"]["hostvars"]["backend-0-0"]["stacki_managed"] == True

		# Check that our added attributes exist
		assert inventory["_meta"]["hostvars"]["frontend-0-0"]["stacki_foo"] == "frontend"
		assert inventory["_meta"]["hostvars"]["backend-0-0"]["stacki_bar"] == "backend"

	def test_vm_attributes(self, add_hypervisor, add_vm, host):
		"""
		Test the plugin creates vars for VM host information
		"""

		result = host.run("ansible-inventory --list")
		assert result.rc == 0
		inventory = json.loads(result.stdout)

		# Check basic VM related data is added
		assert inventory["_meta"]["hostvars"]["vm-backend-0-3"]["stacki_vm_cpu"] == 1
		assert inventory["_meta"]["hostvars"]["vm-backend-0-3"]["stacki_vm_memory"] == 2048
		assert inventory["_meta"]["hostvars"]["vm-backend-0-3"]["stacki_vm_hypervisor"] == "hypervisor-0-1"

		# Check for VM storage info
		assert inventory["_meta"]["hostvars"]["vm-backend-0-3"]["stacki_vm_disk_sda_name"] == "sda"
		assert inventory["_meta"]["hostvars"]["vm-backend-0-3"]["stacki_vm_disk_sda_size"] == 100
		assert inventory["_meta"]["hostvars"]["vm-backend-0-3"]["stacki_vm_disk_sda_image"] == "vm-backend-0-3_disk1.qcow2"
		assert inventory["_meta"]["hostvars"]["vm-backend-0-3"]["stacki_vm_disk_sda_location"] == "/export/pools/stacki/vm-backend-0-3"
		assert inventory["_meta"]["hostvars"]["vm-backend-0-3"]["stacki_vm_disk_sda_mountpoint"] == None
		assert inventory["_meta"]["hostvars"]["vm-backend-0-3"]["stacki_vm_disk_sda_type"] == "disk"
