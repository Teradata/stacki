import json
import pytest
from collections import namedtuple

class TestSetVmStorageLocation:
	def test_no_vm(self, host):
		result = host.run('stack set vm storage location')
		assert result.rc != 0 and 'argument is required' in result.stderr

	def test_no_parameters(self, add_hypervisor, add_vm, host):
		result = host.run('stack set vm storage location vm-backend-0-3')
		assert result.rc != 0 and 'parameter is required' in result.stderr

	def test_invalid_vm(self, host):
		result = host.run('stack set vm storage location fake-backend-0-0 disk=sda location=/export/pools/stacki2')
		assert result.rc != 0 and 'cannot resolve host' in result.stderr

	Disk = namedtuple('param', 'name loc msg')

	# We assume vm-backend-0-3 lacks a third disk
	INVALID_PARAMS = [
		Disk('', '', 'not a valid disk'),
		Disk('', '/export/stack/pools/stacki2', 'not a valid disk'),
		Disk('sdc', '/export/stack/pools/stacki2', 'not a valid disk')
	]

	@pytest.mark.parametrize('params', INVALID_PARAMS)
	def test_invalid_parameters(self, add_hypervisor, add_vm, host, params):
		result = host.run(f'stack set vm storage location vm-backend-0-3 disk={params.name} location={params.loc}')
		assert result.rc != 0 and params.msg in result.stderr

	VALID_PARAMS = [
		Disk('sda', '/export/stack/pools/stacki2', ''),
		Disk('sda', '', '')
	]

	@pytest.mark.parametrize('params', VALID_PARAMS)
	def test_single_host(self, add_hypervisor, add_vm_multiple, host, params):
		result = host.run(f'stack set vm storage location vm-backend-0-3 disk={params.name} location={params.loc}')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list vm storage vm-backend-0-3 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'Virtual Machine': 'vm-backend-0-3',
			'Name': params.name,
			'Type': 'disk',
			'Location': params.loc,
			'Size': 100,
			'Image Name': 'vm-backend-0-3_disk1.qcow2',
			'Image Archive': None,
			'Mountpoint': None,
			'Pending Deletion': False
		}]
