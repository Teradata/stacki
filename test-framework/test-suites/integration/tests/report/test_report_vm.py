import pytest
import re
import json
from pathlib import Path
from tempfile import TemporaryDirectory

class TestReportVM:
	"""
	Tests for the report vm command
	"""

	GOOD_REPORT_VM_DATA = [
	('', 'vm_config_all'),
	('vm-backend-0-3 bare=y', 'vm_config_single'),
	('vm-backend-0-3 vm-backend-0-4 vm-backend-0-5', 'vm_config_multiple'),
	('vm-backend-0-3 vm-backend-0-4 vm-backend-0-5 hypervisor=hypervisor-0-2', 'vm_config_hypervisor'),
	]

	@pytest.mark.parametrize('params, output_file', GOOD_REPORT_VM_DATA)
	def test_report_vm(
		self,
		add_hypervisor,
		add_vm_multiple,
		host,
		host_os,
		params,
		output_file,
		test_file,
	):
		"""
		Test valid input results
		in the expected config
		output

		Can be SUX formatted
		or bare for feeding into
		the hypervisor.
		"""

		expect_output = Path(test_file(f'report/{output_file}_{host_os}.txt')).read_text()

		config_result = host.run(f'stack report vm {params}' )
		assert config_result.rc == 0

		# The uuid of the config will change every time,
		# zero it out so the configs will always match
		# to what we expect
		sub_uuid = re.sub(
			r'<uuid>.*</uuid>',
			'<uuid>00000000-0000-0000-0000-0000000000</uuid>',
			config_result.stdout
		)

		# Now they can be compared
		assert sub_uuid == expect_output

	BAD_LIST_VM_DATA = [
	('backend-0-0', 'not a valid virtual machine'),
	('hypervisor=backend-0-0', 'not a valid hypervisor'),
	('vm-backend-0-1 hypervisor=hypervisor-0-3', 'cannot resolve host'),
	('fake-backend-0-0', 'cannot resolve host'),
	('hypervisor=hypervisor-0-3', 'cannot resolve host'),
	]

	@pytest.mark.parametrize('params, msg', BAD_LIST_VM_DATA)
	def test_report_vm_bad_input(self, add_hypervisor, add_vm_multiple, add_host, host, params, msg):
		"""
		Test with various bad input
		"""

		config_result = host.run(f'stack report vm {params}')
		assert config_result.rc != 0 and msg in config_result.stderr

	def test_report_vm_bad_network(self, add_hypervisor, add_vm_multiple, host):
		"""
		Test report vm raises a command error
		when a virtual machine has an interface
		on a network the hypervisor lacks
		"""

		error_msg = 'not find interface for network public on hypervisor hypervisor-0-1'

		# Add a new network then assign it to a virtual machine
		add_network = host.run('stack add network public address=10.1.1.0 mask=255.255.255.0')
		assert add_network.rc == 0
		set_network = host.run('stack set host interface network vm-backend-0-3 interface=eth0 network=public')
		assert set_network.rc == 0

		# Don't assign an interface on the vm-backend-0-3's hypervisor to the new network
		# and make sure a CommandError is raised with the correct message
		run_report = host.run('stack report vm vm-backend-0-3')
		assert run_report.rc != 0 and error_msg in run_report.stderr

	def test_report_vm_virt_interface(self, add_hypervisor, add_vm_multiple, host, host_os, test_file):
		"""
		Test virtual interfaces for a VM are skipped
		"""

		expect_output = Path(test_file(f'report/vm_config_single_{host_os}.txt')).read_text()

		# Add a new network then assign it to a virtual machine
		add_ipmi_network = host.run('stack add network ipmi address=10.1.1.0 mask=255.255.255.0')
		assert add_ipmi_network.rc == 0

		# Add a new interface to the VM as a virtual interface
		add_ipmi_interface = host.run('stack add host interface vm-backend-0-3 interface=eth0:0 address=10.1.1.2 network=ipmi')
		assert add_ipmi_interface.rc == 0

		run_report = host.run('stack report vm vm-backend-0-3 bare=y')

		# The uuid of the config will change every time,
		# zero it out so the configs will always match
		# to what we expect
		sub_uuid = re.sub(
			r'<uuid>.*</uuid>',
			'<uuid>00000000-0000-0000-0000-0000000000</uuid>',
			run_report.stdout
		)

		assert sub_uuid == expect_output

	def test_report_vm_vlan_interface(self, add_hypervisor, add_vm_multiple, host, host_os, test_file):
		"""
		Test vlan tagged interfaces for a VM are skipped
		"""

		expect_output = Path(test_file(f'report/vm_config_single_{host_os}.txt')).read_text()

		# Add a new network then assign it to a virtual machine
		add_ipmi_network = host.run('stack add network ipmi address=10.1.1.0 mask=255.255.255.0')
		assert add_ipmi_network.rc == 0

		# Add a new interface to the VM as a virtual interface
		add_ipmi_interface = host.run('stack add host interface vm-backend-0-3 interface=eth0.20 address=10.1.1.2 network=ipmi')
		assert add_ipmi_interface.rc == 0

		run_report = host.run('stack report vm vm-backend-0-3 bare=y')

		# The uuid of the config will change every time,
		# zero it out so the configs will always match
		# to what we expect
		sub_uuid = re.sub(
			r'<uuid>.*</uuid>',
			'<uuid>00000000-0000-0000-0000-0000000000</uuid>',
			run_report.stdout
		)

		assert sub_uuid == expect_output

	def test_report_vm_gen_mac(self, add_hypervisor, add_vm, host):
		"""
		Test that when a VM host interface
		lacks a MAC address, the report
		command will generate one and assign it
		"""

		# Add an interface sans MAC address
		add_int = host.run('stack add host interface vm-backend-0-3 ip=192.168.0.2 interface=eth0 default=y network=private')
		assert add_int.rc == 0

		# Run report vm
		get_config = host.run('stack report vm vm-backend-0-3')
		assert get_config.rc == 0

		# Get the MAC address from the config
		find_mac = re.search('<mac address="(?P<mac>.*)"/>', get_config.stdout)
		assert find_mac != None

		mac_addr = find_mac.group('mac')

		# Finally check if the mac address
		# was set in the host interface
		mac_addr = find_mac.group('mac')

		interface_check = host.run('stack list host interface vm-backend-0-3 output-format=json')
		assert interface_check.rc == 0

		interface = json.loads(interface_check.stdout)
		assert interface[0]['mac'] == mac_addr

	def test_report_vm_disk_images(
		self,
		add_hypervisor,
		add_vm_multiple,
		create_image_files,
		add_vm_storage,
		test_file,
		host,
		host_os
	):
		"""
		Test report vm's handling
		of all the different storage
		types: volumes, images,
		and mountpoints
		"""

		tmp_dir = TemporaryDirectory()
		images = create_image_files(tmp_dir)
		add_vm_storage(images, 'vm-backend-0-3')
		expect_output = Path(test_file(f'report/vm_config_storage_{host_os}.txt')).read_text()
		conf = host.run('stack report vm vm-backend-0-3')
		assert conf.rc == 0

		# Remove the generated UUID
		# as it is different each
		# test run
		sub_uuid = re.sub(
			r'<uuid>.*</uuid>',
			'<uuid>00000000-0000-0000-0000-0000000000</uuid>',
			conf.stdout
		)

		assert sub_uuid == expect_output
