import pytest
import json
from pathlib import Path

class TestListVM:
	"""
	Tests for the list vm command
	"""

	def test_list_vm_all(self, add_hypervisor, add_vm_multiple, host):
		list_result = host.run(f'stack list vm output-format=json')
		assert list_result.rc == 0

		assert json.loads(list_result.stdout) == [
			{
				'virtual machine': 'vm-backend-0-3',
				'hypervisor': 'hypervisor-0-1',
				'memory': 2048,
				'cpu': 1,
				'pending deletion': False
			},
			{
				'virtual machine': 'vm-backend-0-4',
				'hypervisor': 'hypervisor-0-1',
				'memory': 2048,
				'cpu': 2,
				'pending deletion': False
			},
			{
				'virtual machine': 'vm-backend-0-5',
				'hypervisor': 'hypervisor-0-2',
				'memory': 3072,
				'cpu': 3,
				'pending deletion': False
			},
			{
				'virtual machine': 'vm-backend-0-6',
				'hypervisor': 'hypervisor-0-2',
				'memory': 4096,
				'cpu': 4,
				'pending deletion': False
			}
		]

	def test_list_vm_single(self, add_hypervisor, add_vm_multiple, host):
		list_result = host.run(f'stack list vm vm-backend-0-3 output-format=json')
		assert list_result.rc == 0

		assert json.loads(list_result.stdout) == [
			{
				'virtual machine': 'vm-backend-0-3',
				'hypervisor': 'hypervisor-0-1',
				'memory': 2048,
				'cpu': 1,
				'pending deletion': False
			}
		]


	def test_list_vm_multiple(self, add_hypervisor, add_vm_multiple, host):
		list_result = host.run(f'stack list vm vm-backend-0-3 vm-backend-0-5 vm-backend-0-6 output-format=json')
		assert list_result.rc == 0

		assert json.loads(list_result.stdout) == [
			{
				'virtual machine': 'vm-backend-0-3',
				'hypervisor': 'hypervisor-0-1',
				'memory': 2048,
				'cpu': 1,
				'pending deletion': False
			},
			{
				'virtual machine': 'vm-backend-0-5',
				'hypervisor': 'hypervisor-0-2',
				'memory': 3072,
				'cpu': 3,
				'pending deletion': False
			},
			{
				'virtual machine': 'vm-backend-0-6',
				'hypervisor': 'hypervisor-0-2',
				'memory': 4096,
				'cpu': 4,
				'pending deletion': False
			}
		]

	def test_list_vm_hypervisor(self, add_hypervisor, add_vm_multiple, host):
		list_result = host.run(f'stack list vm vm-backend-0-3 vm-backend-0-5 vm-backend-0-6 hypervisor=hypervisor-0-2 output-format=json')
		assert list_result.rc == 0

		assert json.loads(list_result.stdout) == [
			{
				'virtual machine': 'vm-backend-0-5',
				'hypervisor': 'hypervisor-0-2',
				'memory': 3072,
				'cpu': 3,
				'pending deletion': False
			},
			{
				'virtual machine': 'vm-backend-0-6',
				'hypervisor': 'hypervisor-0-2',
				'memory': 4096,
				'cpu': 4,
				'pending deletion': False
			}
		]

	def test_list_vm_expanded(self, add_hypervisor, add_vm_multiple, host):
		list_result = host.run(f'stack list vm vm-backend-0-3 vm-backend-0-5 vm-backend-0-6 expanded=y output-format=json')
		assert list_result.rc == 0

		assert json.loads(list_result.stdout) == [
			{
				'virtual machine': 'vm-backend-0-3',
				'hypervisor': 'hypervisor-0-1',
				'memory': 2048,
				'cpu': 1,
				'pending deletion': False,
				'status': 'Connection failed to hypervisor'
			},
			{
				'virtual machine': 'vm-backend-0-5',
				'hypervisor': 'hypervisor-0-2',
				'memory': 3072,
				'cpu': 3,
				'pending deletion': False,
				'status': 'Connection failed to hypervisor'
			},
			{
				'virtual machine': 'vm-backend-0-6',
				'hypervisor': 'hypervisor-0-2',
				'memory': 4096,
				'cpu': 4,
				'pending deletion': False,
				'status': 'Connection failed to hypervisor'
			}
		]


	BAD_LIST_VM_DATA = [
	('backend-0-0', 'not a valid virtual machine'),
	('hypervisor=backend-0-0', 'not a valid hypervisor'),
	('vm-backend-0-1 hypervisor=hypervisor-0-3', 'cannot resolve host'),
	('fake-backend-0-0', 'cannot resolve host'),
	('hypervisor=hypervisor-0-3', 'cannot resolve host')
	]

	@pytest.mark.parametrize('params, msg', BAD_LIST_VM_DATA)
	def test_list_vm_bad(self, add_hypervisor, add_vm_multiple, add_host, host, params, msg):
		list_result = host.run(f'stack list vm {params}')
		assert list_result.rc != 0 and msg in list_result.stderr
