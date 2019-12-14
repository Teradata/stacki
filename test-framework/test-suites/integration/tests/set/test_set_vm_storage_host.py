import json
import pytest
from collections import namedtuple
from tempfile import TemporaryDirectory

class TestSetVmStorageHost:
	def test_no_vm(self, host):
		result = host.run('stack set vm storage host')
		assert result.rc != 0 and 'argument is required' in result.stderr

	def test_no_parameters(self, add_hypervisor, add_vm, host):
		result = host.run('stack set vm storage host vm-backend-0-3')
		assert result.rc != 0 and 'parameter is required' in result.stderr

	Disk = namedtuple('disk', 'name new_host msg')

	# Test various bad input:
	# 1. Blank parameters
	# 2. undefined new host
	# 3. undefined disk on the current host
	# 4. When a disk of the same device name
	#    is present on the new host
	INVALID_PARAMS = [
		Disk('', '', ''),
		Disk('sda', 'fake-backend-0-3', 'not a valid virtual host'),
		Disk('sdb', 'vm-backend-0-4', 'not found defined'),
		Disk('sda', 'vm-backend-0-4', 'found already defined')
	]

	@pytest.mark.parametrize('params', INVALID_PARAMS)
	def test_invalid_parameters(self, add_hypervisor, add_vm_multiple, host, params):
		cmd = f'stack set vm storage host vm-backend-0-3 disk={params.name} newhost={params.new_host}'
		result = host.run(cmd)
		assert result.rc != 0 and params.msg in result.stderr

	def test_invalid_vm(self, add_hypervisor, add_vm_multiple, host):
		result = host.run('stack set vm storage host fake-backend-0-0 disk=sda newhost=vm_backend-0-4')
		assert result.rc != 0 and 'cannot resolve host' in result.stderr

	# Test moving disk sdb of virtual-backend-0-4
	# to another host with only one disk
	def test_single_host(self, add_hypervisor, add_vm_multiple, host):
		result = host.run('stack set vm storage host vm-backend-0-4 disk=sdb newhost=vm-backend-0-3')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm storage vm-backend-0-3 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'Virtual Machine': 'vm-backend-0-3',
				'Name': 'sda',
				'Type': 'disk',
				'Location': '/export/pools/stacki/vm-backend-0-3',
				'Size': 100,
				'Image Name': 'vm-backend-0-3_disk1.qcow2',
				'Image Archive': None,
				'Mountpoint': None,
				'Pending Deletion': False
			},
			{
				"Virtual Machine": "vm-backend-0-3",
				"Name": "sdb",
				"Type": "disk",
				"Location": "/export/pools/stacki/vm-backend-0-4",
				"Size": 100,
				"Image Name": "vm-backend-0-4_disk2.qcow2",
				"Image Archive": None,
				"Mountpoint": None,
				"Pending Deletion": False
			}
		]

	# Test moving multiple types of disks to different hosts
	def test_multiple_host(self, add_hypervisor, add_vm_multiple, add_vm_storage, create_image_files, host):
		temp_dir = TemporaryDirectory()
		disks = create_image_files(temp_dir)

		# Add several image and mount based
		# images to vm-backend-0-4
		add_vm_storage(disks, 'vm-backend-0-4')
		result = host.run('stack list vm storage vm-backend-0-4 output-format=json')

		result = host.run('stack set vm storage host vm-backend-0-4 disk=sde newhost=vm-backend-0-3')
		assert result.rc == 0

		result = host.run('stack set vm storage host vm-backend-0-4 disk=sdh newhost=vm-backend-0-3')
		assert result.rc == 0

		result = host.run('stack list vm storage vm-backend-0-3 output-format=json')
		assert result.rc == 0

		assert json.loads(result.stdout) == [
			{
				'Virtual Machine': 'vm-backend-0-3',
				'Name': 'sda',
				'Type': 'disk',
				'Location': '/export/pools/stacki/vm-backend-0-3',
				'Size': 100,
				'Image Name': 'vm-backend-0-3_disk1.qcow2',
				'Image Archive': None,
				'Mountpoint': None,
				'Pending Deletion': False
			},
			{
				"Virtual Machine": "vm-backend-0-3",
				"Name": "sde",
				"Type": "image",
				"Location": '/export/pools/stacki/vm-backend-0-4',
				"Size": None,
				"Image Name": "image3.qcow2",
				"Image Archive": str(disks['image3.qcow2']),
				"Mountpoint": None,
				"Pending Deletion": False
			},
			{
				"Virtual Machine": "vm-backend-0-3",
				"Name": "sdh",
				"Type": "mountpoint",
				"Location": "/export/pools/stacki/vm-backend-0-4",
				"Size": None,
				"Image Name": '',
				"Image Archive": None,
				"Mountpoint": '/dev/sdb',
				"Pending Deletion": False
			}
		]
