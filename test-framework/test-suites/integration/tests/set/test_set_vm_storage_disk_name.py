import json
import pytest
from collections import namedtuple
from tempfile import TemporaryDirectory

class TestSetVmStorageName:
	def test_no_vm(self, host):
		result = host.run('stack set vm storage name')
		assert result.rc != 0

	def test_no_parameters(self, add_hypervisor, add_vm, host):
		result = host.run('stack set vm storage name vm-backend-0-3')
		assert result.rc != 0

	Disk = namedtuple('disk', 'backing name msg')
	INVALID_PARAMS = [
		Disk('', '', 'not found for'),
		Disk('fake_disk.qcow2', 'sda', 'not found for'),
	]
	@pytest.mark.parametrize('params', INVALID_PARAMS)
	def test_invalid_parameters(self, add_hypervisor, add_vm, host, params):
		result = host.run(f'stack set vm storage name vm-backend-0-3 backing={params.backing} name={params.name}')
		assert result.rc != 0 and params.msg in result.stderr

	def test_disk_already_defined(self, add_hypervisor, add_vm, add_vm_storage, create_image_files, host):
		temp_dir = TemporaryDirectory()
		disks = create_image_files(temp_dir)
		add_storage = add_vm_storage(disks, 'vm-backend-0-3')
		result = host.run(f'stack set vm storage name vm-backend-0-3 backing={disks["image2.qcow2"]} name=sda')
		assert result.rc != 0 and 'already exists for' in result.stderr

	def test_invalid_vm(self, host):
		result = host.run('stack set vm storage name fake-backend-0-0 backing=images.qcow2 name=sda')
		assert result.rc != 0 and 'cannot resolve host' in result.stderr

	def test_single_host(self, add_hypervisor, add_vm_multiple, host):
		result = host.run('stack set vm storage name vm-backend-0-3 backing=vm-backend-0-3_disk1.qcow2 name=sdb')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm storage vm-backend-0-3 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'Virtual Machine': 'vm-backend-0-3',
			'Name': 'sdb',
			'Type': 'disk',
			'Location': '/export/pools/stacki/vm-backend-0-3',
			'Size': 100,
			'Image Name': 'vm-backend-0-3_disk1.qcow2',
			'Mountpoint': None,
			'Pending Deletion': False
		}]

	def test_host_multiple_disk(
		self,
		add_hypervisor,
		add_vm_multiple,
		add_vm_storage,
		create_image_files,
		host
	):
		temp_dir = TemporaryDirectory()
		disks = create_image_files(temp_dir)
		add_vm_storage(disks, 'vm-backend-0-3')

		# Change the disk names of all three
		# types of storage backings
		result = host.run('stack set vm storage name vm-backend-0-3 backing=vm-backend-0-3_disk1.qcow2 name=sde')
		assert result.rc == 0

		result = host.run(f'stack set vm storage name vm-backend-0-3 backing={disks["image1.raw"]} name=sda')
		assert result.rc == 0

		result = host.run('stack set vm storage name vm-backend-0-3 backing=/dev/sdb name=sdb')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm storage vm-backend-0-3 output-format=json')
		assert result.rc == 0
		[
			{
				'Virtual Machine': 'vm-backend-0-3',
				'Name': 'sde',
				'Type': 'disk',
				'Location': '/export/pools/stacki/vm-backend-0-3',
				'Size': 100,
				'Image Name': 'vm-backend-0-3_disk1.qcow2',
				'Mountpoint': None,
				'Pending Deletion': False
			},
			{
				'Virtual Machine': 'vm-backend-0-3',
				'Name': 'sda',
				'Type': 'image',
				'Location': '/export/pools/stacki/vm-backend-0-3',
				'Size': None,
				'Image Name': f'{disks["image1.raw"]}',
				'Mountpoint': None,
				'Pending Deletion': False
			},
			{
				'Virtual Machine': 'vm-backend-0-3',
				'Name': 'sdc',
				'Type': 'image',
				'Location': '/export/pools/stacki/vm-backend-0-3',
				'Size': None,
				'Image Name': f'{disks["image2.qcow2"]}',
				'Mountpoint': None, 'PendingDeletion': False
			},
			{
				'Virtual Machine': 'vm-backend-0-3',
				'Name': 'sdb',
				'Type': 'mountpoint',
				'Location': None,
				'Size': None,
				'Image Name': None,
				'Mountpoint': '/dev/sdb',
				'Pending Deletion': False
			}
		]

	def test_disk_swap(self, add_hypervisor, add_vm_multiple, host):

		# Set the first disk to blank to allow the disks to be swapped
		# if a new disk name is already set, the disk cannot be swapped
		result = host.run('stack set vm storage name vm-backend-0-4 backing=vm-backend-0-4_disk1.qcow2 name=')
		assert result.rc == 0

		result = host.run('stack set vm storage name vm-backend-0-4 backing=vm-backend-0-4_disk2.qcow2 name=sda')
		assert result.rc == 0

		result = host.run('stack set vm storage name vm-backend-0-4 backing=vm-backend-0-4_disk1.qcow2 name=sdb')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm storage vm-backend-0-4 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'Virtual Machine': 'vm-backend-0-4',
				'Name': 'sdb',
				'Type': 'disk',
				'Location': '/export/pools/stacki/vm-backend-0-4',
				'Size': 200,
				'Image Name': 'vm-backend-0-4_disk1.qcow2',
				'Mountpoint': None,
				'Pending Deletion': False
			},
			{
				'Virtual Machine': 'vm-backend-0-4',
				'Name': 'sda',
				'Type': 'disk',
				'Location': '/export/pools/stacki/vm-backend-0-4',
				'Size': 100,
				'Image Name': 'vm-backend-0-4_disk2.qcow2',
				'Mountpoint': None,
				'Pending Deletion': False
			}
		]

	def test_disk_same_image(self, add_hypervisor, add_vm_multiple, create_image_files, host):
		"""
		Test when a disk image is used for multiple hosts, only the
		given host's disk name is changed
		"""

		temp_dir = TemporaryDirectory()
		disks = create_image_files(temp_dir)

		# Add image1.raw to vmbackend-0-3 and vm-backend-0-4
		add_storage = host.run(f'stack add vm storage vm-backend-0-3 disks={disks["image1.raw"]} storage_pool=/export/pools/stacki')
		assert add_storage.rc == 0

		add_storage = host.run(f'stack add vm storage vm-backend-0-4 disks={disks["image1.raw"]} storage_pool=/export/pools/stacki')
		assert add_storage.rc == 0

		# Set only vm-backend-0-4's disk name to vdc
		result = host.run(f'stack set vm storage name vm-backend-0-4 backing={disks["image1.raw"]} name=vdc')
		assert result.rc == 0

		# Check vm-backend-0-3 doesn't have the disk name change
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
				'Mountpoint': None,
				'Pending Deletion': False
			},
			{
				'Virtual Machine': 'vm-backend-0-3',
				'Name': 'sdb',
				'Type': 'image',
				'Location': '/export/pools/stacki/vm-backend-0-3',
				'Size': None,
				'Image Name': f'{disks["image1.raw"]}',
				'Mountpoint': None,
				'Pending Deletion': False
			}
		]
