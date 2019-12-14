import pytest
import json
import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory

class TestAddVMStorage:
	"""
	Tests for adding new virtual machine
	storage
	"""

	STOR_POOL = '/export/pools/stacki'

	def test_add_vm_storage_simple(self, add_hypervisor, add_vm, host, test_file, create_image_files):
		"""
		Test adding a new volume and raw image
		"""

		image_dir = TemporaryDirectory()
		images = create_image_files(image_dir)
		image_name = images["image4.raw"]

		# Adds an uncompressed qcow2 image to the host
		add_storage = f'stack add vm storage vm-backend-0-3 storage_pool={self.STOR_POOL} disks={images["image4.raw"]}'
		storage_result = host.run(add_storage)
		assert storage_result.rc == 0

		list_result = host.run(f'stack list vm storage output-format=json')
		assert list_result.rc == 0

		assert json.loads(list_result.stdout) == [
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
				'Virtual Machine': 'vm-backend-0-3',
				'Name': 'sdb',
				'Type': 'image',
				'Location': '/export/pools/stacki/vm-backend-0-3',
				'Size': None,
				'Image Name': str(image_name),
				'Image Archive': None,
				'Mountpoint': None,
				'Pending Deletion': False
				}
		]

	def test_add_vm_storage_complex(self, add_hypervisor, add_vm, host, test_file, create_image_files):
		"""
		Test for adding every type
		of storage medium accepted
		by add vm storage
		"""

		image_dir = TemporaryDirectory()
		expect_file = Path(test_file(f'add/add_vm_storage_complex.json'))
		expect_output = json.loads(expect_file.read_text())
		images = create_image_files(image_dir)
		disks = []

		for image, loc in images.items():

			# If an archive contains
			# mutliple images, we only need
			# to add the archive once
			# when running add vm storage
			if str(loc) in disks:
				continue
			disks.append(str(loc))

		# Populate the output with the
		# tmpdir locations of each image
		# which changes with each test run
		for disk in expect_output:
			if disk['Type'] != 'image':
				continue
			disk_name = disk['Image Name']
			if disk_name in images:
				image = images[disk_name]
				if tarfile.is_tarfile(image) or '.gz' in image.suffixes:
					disk['Image Archive'] = str(images[disk_name])
				else:
					disk['Image Name'] = str(images[disk_name])

		add_storage = f'stack add vm storage vm-backend-0-3 storage_pool={self.STOR_POOL} disks=200,{",".join(disks)},/dev/sdb'
		storage_result = host.run(add_storage)
		assert storage_result.rc == 0

		list_result = host.run(f'stack list vm storage output-format=json')
		assert list_result.rc == 0

		actual_output = json.loads(list_result.stdout)
		assert expect_output == actual_output

	def test_add_vm_storage_bad(self, add_hypervisor, add_vm, host, create_image_files, create_invalid_image):
		"""
		Test adding storage with bad input
		"""

		temp_dir = TemporaryDirectory()
		valid_images = create_image_files(temp_dir)
		invalid_image = create_invalid_image(temp_dir)

		add_stor_disk = host.run(f'stack add vm storage vm-backend-0-3 disks=200')
		assert add_stor_disk.rc != 0 and 'parameter needed for' in add_stor_disk.stderr

		add_stor_tar = host.run(f'stack add vm storage vm-backend-0-3 disks={valid_images["image.qcow2"]}')
		assert add_stor_disk.rc != 0 and 'parameter needed for' in add_stor_disk.stderr

		add_stor_image = host.run(f'stack add vm storage vm-backend-0-3 disks={valid_images["image5.qcow2"]}')
		assert add_stor_disk.rc != 0 and 'parameter needed for' in add_stor_disk.stderr

		add_stor_invalid = host.run(f'stack add vm storage vm-backend-0-3 disks={invalid_image}')
		assert add_stor_disk.rc != 0 and 'parameter needed for' in add_stor_disk.stderr
