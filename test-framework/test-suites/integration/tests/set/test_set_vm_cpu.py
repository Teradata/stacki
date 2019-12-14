import json
import pytest

class TestSetVmCPU:
	def test_no_vm(self, host):
		result = host.run('stack set vm cpu')
		assert result.rc != 0

	def test_no_parameters(self, add_hypervisor, add_vm, host):
		result = host.run('stack set vm cpu vm-backend-0-3')
		assert result.rc != 0

	INVALID_PARAMS = [
		('', 'parameter must be'),
		('-1', 'parameter must be'),
		('0', 'parameter must be'),
		('3.5', 'parameter must be')
	]

	@pytest.mark.parametrize('params, msg', INVALID_PARAMS)
	def test_invalid_parameters(self, add_hypervisor, add_vm, host, params, msg):
		result = host.run(f'stack set vm cpu vm-backend-0-3 cpu={params}')
		assert result.rc != 0 and msg in result.stderr

	def test_invalid_vm(self, host):
		result = host.run('stack set vm cpu fake-backend-0-0 cpu=2')
		assert result.rc != 0

	def test_single_host(self, add_hypervisor, add_vm, host):
		result = host.run('stack set vm cpu vm-backend-0-3  cpu=4')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm vm-backend-0-3 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'virtual machine': 'vm-backend-0-3',
			'hypervisor': 'hypervisor-0-1',
			'memory': 2048,
			'cpu': 4,
			'pending deletion': False
		}]

	def test_multiple_hosts(self, add_hypervisor, add_vm_multiple, host):

		result = host.run('stack set vm cpu vm-backend-0-3 vm-backend-0-4 cpu=4')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm vm-backend-0-3 vm-backend-0-4 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'virtual machine': 'vm-backend-0-3',
				'hypervisor': 'hypervisor-0-1',
				'memory': 2048,
				'cpu': 4,
				'pending deletion': False
			},
			{
				'virtual machine': 'vm-backend-0-4',
				'hypervisor': 'hypervisor-0-1',
				'memory': 2048,
				'cpu': 4,
				'pending deletion': False
			}
		]
