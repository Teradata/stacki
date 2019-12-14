import json
import pytest
from tempfile import TemporaryDirectory

class TestRemoveVmStorage:

	REMOVE_VM_BAD_DATA = [
		('', '', 'argument is required'),
		('fake-backend-0-0', 'disk=sda', 'cannot resolve host'),
		('vm-backend-0-3', 'disk=sde', 'not a defined disk')
	]
	@pytest.mark.parametrize('hostname, params, msg', REMOVE_VM_BAD_DATA)
	def test_bad_input(self, host, add_hypervisor, add_vm, hostname, params, msg):
		result = host.run(f'stack remove vm storage {hostname} {params}')
		assert result.rc != 0 and msg in result.stderr

	def test_single_host(self, add_hypervisor, add_vm, host):
		result = host.run('stack remove vm storage vm-backend-0-3 disk=sda')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm storage vm-backend-0-3 output-format=json')
		assert result.rc == 0

		assert json.loads(result.stdout) == [{
			'Virtual Machine': 'vm-backend-0-3',
			'Name': 'sda',
			'Type': 'disk',
			'Location': '/export/pools/stacki/vm-backend-0-3',
			'Size': 100,
			'Image Name': 'vm-backend-0-3_disk1.qcow2',
			'Mountpoint': None,
			'Pending Deletion': True
		}]

	@pytest.mark.parametrize('disk', ['sdb', 'sdc', 'sdd'])
	def test_multiple_disks(self, add_hypervisor, add_vm, create_image_files, add_vm_storage, disk, host):
		"""
		Remove different disks from a host
		"""

		tmp_dir = TemporaryDirectory()
		images = create_image_files(tmp_dir)
		add_vm_storage(images, 'vm-backend-0-3')

		result = host.run(f'stack remove vm storage vm-backend-0-3 disk={disk}')
		assert result.rc == 0

		result = host.run(f'stack list vm storage vm-backend-0-3 output-format=json')
		assert result.rc == 0

		for disk in json.loads(result.stdout):
			if disk['Name'] == disk:
				assert disk['Pending Deletion']
