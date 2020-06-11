import pytest
import time
import json
import tempfile
from pathlib import Path

class TestLoadVM:

	"""
	Test loading virtual machine info
	via stack load
	"""

	def test_load_vm(
		self,
		add_hypervisor,
		add_vm_multiple,
		host,
		stack_load,
		revert_etc
	):
		"""
		Test stack load with a focus on virtual machine information.
		"""

		# Dump our vm information
		results = host.run('stack dump vm')
		assert results.rc == 0

		# Save dumped data to compare later
		dumped_vm = json.loads(results.stdout)

		# Write to a temp file to load in later
		vm_dump = tempfile.NamedTemporaryFile(mode='w+')
		vm_dump.write(results.stdout)

		# Needed as otherwise stack load finds
		# a blank text file
		vm_dump.seek(0)

		# Dump our host information
		results = host.run('stack dump host')
		assert results.rc == 0

		# Write to a temp file to load in later
		host_dump = tempfile.NamedTemporaryFile(mode='w+')
		host_dump.write(results.stdout)

		# Needed as otherwise stack load finds
		# a blank text file
		host_dump.seek(0)

		# Remove the existing virtual machines
		remove_vm_hosts = host.run('stack remove host vm-backend-0-3 vm-backend-0-4 vm-backend-0-5 vm-backend-0-6')
		assert remove_vm_hosts.rc == 0

		load_host_data = stack_load(host_dump.name)
		assert load_host_data.rc == 0

		# Load our host data back in
		# It's ok if load throws some errors so skip
		# checking the return code
		load_vm_data = stack_load(vm_dump.name)

		dump_vm_data = host.run('stack dump vm')
		assert dump_vm_data.rc == 0

		# Load our vm data back in
		loaded = json.loads(dump_vm_data.stdout)

		# Check the output of dump vm is what we expected
		assert loaded == dumped_vm

	def test_load_vm_storage(
		self,
		add_hypervisor,
		add_vm,
		create_image_files,
		add_vm_storage,
		stack_load,
		host,
		revert_etc
	):
		"""
		Test loading a VM with all types of storage mediums
		"""

		tempdir = tempfile.TemporaryDirectory()
		images = create_image_files(tempdir)
		add_vm_storage(images, 'vm-backend-0-3')

		# Dump our vm information
		results = host.run('stack dump vm')
		assert results.rc == 0

		dumped = json.loads(results.stdout)

		# Write to a temp file to load in later
		vm_dump_file = tempfile.NamedTemporaryFile(mode='w+')
		vm_dump_file.write(results.stdout)
		vm_dump_file.seek(0)

		# Dump our host information
		results = host.run('stack dump host')
		assert results.rc == 0

		# Write to a temp file to load in later
		host_dump_file = tempfile.NamedTemporaryFile(mode='w+')
		host_dump_file.write(results.stdout)
		host_dump_file.seek(0)

		remove_vm = host.run('stack remove host vm-backend-0-3')
		assert remove_vm.rc == 0

		# Load our host data back in
		# It's ok if load throws some errors so skip
		# checking the return code
		load_host_data = stack_load(host_dump_file.name)

		# Load our vm data back in
		load_vm_data = stack_load(vm_dump_file.name)

		dump_vm_data = host.run('stack dump vm')
		assert dump_vm_data.rc == 0

		loaded = json.loads(dump_vm_data.stdout)

		# Check the output of dump vm is what we expected
		assert loaded == dumped

	def test_load_vm_duplicate(
		self,
		add_hypervisor,
		add_vm,
		stack_load,
		host
	):
		"""
		Test loading the same vm dump file twice
		and ensure no new hosts or storage are added
		"""

		# Dump our vm information
		results = host.run('stack dump vm')
		assert results.rc == 0

		dumped = json.loads(results.stdout)

		# Write to a temp file to load in later
		vm_dump_file = tempfile.NamedTemporaryFile(mode='w+')
		vm_dump_file.write(results.stdout)
		vm_dump_file.seek(0)

		# Load our vm data back in
		load_vm_data = stack_load(vm_dump_file.name)

		dump_vm_data = host.run('stack dump vm')
		assert dump_vm_data.rc == 0

		loaded = json.loads(dump_vm_data.stdout)

		# Make sure no additional disks or vm hosts
		# were added
		assert loaded == dumped

	def test_load_vm_no_disk(
		self,
		add_hypervisor,
		add_vm,
		stack_load,
		test_file,
		host
	):
		"""
		Test loading storage for a VM host
		where the image file is not present on the frontend
		"""

		# Dump our vm information
		results = host.run('stack dump vm')
		assert results.rc == 0

		dumped = json.loads(results.stdout)

		# Get dump that contains a valid VM host but with a qcow2 file
		# not present on the frontend
		load_bogus_data = stack_load(test_file('load/json/vm_no_disk.json'))

		dump_vm_data = host.run('stack dump vm')
		assert dump_vm_data.rc == 0

		loaded = json.loads(dump_vm_data.stdout)

		# Ensure no new storage was added to the host
		assert loaded == dumped
