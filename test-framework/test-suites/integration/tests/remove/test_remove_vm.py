import json
import pytest
from tempfile import TemporaryDirectory

class TestRemoveVM:

	REMOVE_VM_BAD_DATA = [
		('', 'argument is required'),
		('fake-backend-0-0', 'cannot resolve host'),
		('backend-0-0', 'not a valid virtual machine')
	]
	@pytest.mark.parametrize('hostname, msg', REMOVE_VM_BAD_DATA)
	def test_bad_input(self, host, add_host, hostname, msg):
		result = host.run(f'stack remove vm {hostname}')
		assert result.rc != 0 and msg in result.stderr

	def test_dont_remove_frontend_vm(self, host, add_hypervisor):

		# Add the frontend as a virtual machine
		add_cmd = 'stack add vm frontend-0-0 hypervisor=hypervisor-0-1 storage_pool=/export/pools/stacki'
		add_frontend_vm = host.run(add_cmd)
		assert add_frontend_vm.rc == 0

		# Ensure the frontend cannot be removed as a virtual machine
		remove_frontend_vm = host.run('stack remove vm frontend-0-0')
		assert remove_frontend_vm.rc != 0

	def test_invalid_host(self, host):
		result = host.run('stack remove vm fake-backend-0-0')
		assert result.rc != 0

	def test_no_vm(self, host, add_host):
		result = host.run('stack remove vm backend-0-0')
		assert result.rc != 0

	def test_single_host(self, add_hypervisor, add_vm, host):
		result = host.run('stack remove vm vm-backend-0-3')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm vm-backend-0-3 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'virtual machine': 'vm-backend-0-3',
			'hypervisor': 'hypervisor-0-1',
			'memory': 2048,
			'cpu': 1,
			'pending deletion': True
		}]

	def test_multiple_hosts(self, add_hypervisor, add_vm_multiple, host):
		result = host.run('stack remove vm vm-backend-0-3 vm-backend-0-4')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm vm-backend-0-3 vm-backend-0-4 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'virtual machine': 'vm-backend-0-3',
				'hypervisor': 'hypervisor-0-1',
				'memory': 2048,
				'cpu': 1,
				'pending deletion': True
			},
			{
				'virtual machine': 'vm-backend-0-4',
				'hypervisor': 'hypervisor-0-1',
				'memory': 2048,
				'cpu': 2,
				'pending deletion': True
			}
		]

	def test_nukedisks(self, add_hypervisor, add_vm_multiple, add_vm_storage, host, create_image_files, test_file):
		tmp_dir = TemporaryDirectory()
		images = create_image_files(tmp_dir)
		add_vm_storage(images, 'vm-backend-0-3')

		result = host.run('stack remove vm vm-backend-0-3 nukedisks=y')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm storage vm-backend-0-3 output-format=json')
		assert result.rc == 0

		# Make sure every disk is marked
		# for deletion
		for disk in json.loads(result.stdout):
			assert disk['Pending Deletion']
