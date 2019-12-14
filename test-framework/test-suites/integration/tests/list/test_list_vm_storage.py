import pytest
import json
from pathlib import Path

class TestListStorageVM:

	GOOD_LIST_VM_DATA = [
	('', 'vm_storage_simple.json'),
	('vm-backend-0-3', 'vm_storage_single.json'),
	('vm-backend-0-3 vm-backend-0-5 vm-backend-0-6', 'vm_storage_multiple.json'),
	('vm-backend-0-3 vm-backend-0-5 vm-backend-0-6 hypervisor=hypervisor-0-2', 'vm_storage_hypervisor.json')
	]

	@pytest.mark.parametrize('params, output_file', GOOD_LIST_VM_DATA)
	def test_list_vm_storage_postive(
		self,
		add_hypervisor,
		add_vm_multiple,
		host,
		test_file,
		params,
		output_file
	):
		"""
		Test that the command works when
		valid parameters are called
		"""

		expect_file = Path(test_file(f'list/{output_file}'))
		expect_output = json.loads(expect_file.read_text())

		list_result = host.run(f'stack list vm storage {params} output-format=json')
		assert list_result.rc == 0

		actual_output = json.loads(list_result.stdout)
		assert expect_output == actual_output

	BAD_LIST_VM_DATA = [
	('backend-0-0', 'not a valid virtual machine'),
	('hypervisor=backend-0-0', 'not a valid hypervisor'),
	('vm-backend-0-1 hypervisor=hypervisor-0-3', 'cannot resolve host'),
	('fake-backend-0-0', 'cannot resolve host'),
	('hypervisor=hypervisor-0-3', 'cannot resolve host')
	]

	@pytest.mark.parametrize('params, msg', BAD_LIST_VM_DATA)
	def test_list_vm_negative(
		self,
		add_hypervisor,
		add_vm_multiple,
		add_host,
		host,
		params,
		msg
	):
		"""
		Test the command fails with
		bad input parameters
		"""

		list_result = host.run(f'stack list vm storage {params}')
		assert list_result.rc != 0 and msg in list_result.stderr
