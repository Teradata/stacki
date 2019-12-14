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
	('', 'vm_config_all.txt'),
	('vm-backend-0-3 bare=y', 'vm_config_single.txt'),
	('vm-backend-0-3 vm-backend-0-4 vm-backend-0-5', 'vm_config_multiple.txt'),
	('vm-backend-0-3 vm-backend-0-4 vm-backend-0-5 hypervisor=hypervisor-0-2', 'vm_config_hypervisor.txt')
	]

	@pytest.mark.parametrize('params, output_file', GOOD_REPORT_VM_DATA)
	def test_report_vm(self, add_hypervisor, add_vm_multiple, host, params, output_file, test_file):
		"""
		Test valid input results
		in the expected config
		output

		Can be SUX formatted
		or bare for feeding into
		the hypervisor.
		"""

		expect_output = Path(test_file(f'report/{output_file}')).read_text()

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
	('hypervisor=hypervisor-0-3', 'cannot resolve host')
	]

	@pytest.mark.parametrize('params, msg', BAD_LIST_VM_DATA)
	def test_report_vm_bad_input(self, add_hypervisor, add_vm_multiple, add_host, host, params, msg):
		"""
		Test with various bad input
		"""

		config_result = host.run(f'stack report vm {params}')
		assert config_result.rc != 0 and msg in config_result.stderr

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
		host
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
		expect_output = Path(test_file('report/vm_config_storage.txt')).read_text()
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

	def test_report_vm_config_location(self, add_hypervisor, add_vm_multiple, host):
		set_attr = host.run('stack set host attr hypervisor-0-1 attr="vm.config.location" value="/export/stacki/libvirt/qemu/"')
		assert set_attr.rc == 0

		conf = host.run('stack report vm vm-backend-0-3')
		assert conf.rc == 0

		expect_line = '<stack:file stack:name=/export/stacki/libvirt/qemu/vm-backend-0-3.xml>'
		assert expect_line in conf.stdout
