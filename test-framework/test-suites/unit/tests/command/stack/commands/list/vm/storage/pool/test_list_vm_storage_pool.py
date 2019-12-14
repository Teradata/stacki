import pytest
from unittest.mock import ANY, call, create_autospec, patch
from stack.commands.list.vm.storage.pool import Command, Hypervisor, VmException, ArgError

class TestListVmStoragePool:
	def mock_vm_exception(self, *args, **kwargs):
		raise VmException('Oh no something went wrong!')

	class CommandUnderTest(Command):
		"""
		A class derived from the Command class under test used to override __init__.
		This allows easier instantiation for testing purposes by excluding the base Command
		class initialization code.
		"""

		_params = ()
		def __init__(self):
			pass

	@pytest.fixture
	def command(self):
		"""
		Fixture to create and return a Command class instance for testing.
		"""

		return self.CommandUnderTest()


	# Test different values for the command
	# 1. No hypervisors
	# 2. A single hypervisor with one pool
	# 3. Multiple hypervisors with multiple pools
	POOL_VALUES = [
		{
			'': {
			}
		},
		{
			'hypervisor-foo': {
				'foo': {
					'allocated': '5 GB',
					'available': '30 GB',
					'capacity': '35 GB',
					'is_active': True
				}
			}
		},
		{
			'hypervisor-foo': {
				'foo': {
					'allocated': '40 GB',
					'available': '60 GB',
					'capacity': '100 GB',
					'is_active': True
				},
			},
			'hypervisor-bar': {
				'foo': {
					'allocated': '20 GB',
					'available': '20 GB',
					'capacity': '40 GB',
					'is_active': True
				},
				'bar': {
					'allocated': '4 GB',
					'available': '57 GB',
					'capacity': '61 GB',
					'is_active': True
				},
			},
			'hypervisor-baz': {
				'foo': {
					'allocated': '20 GB',
					'available': '30 GB',
					'capacity': '50 GB',
					'is_active': True
				},
				'bar': {
					'allocated': '0 GB',
					'available': '60 GB',
					'capacity': '60 GB',
					'is_active': True
				},
				'baz': {
					'allocated': '0 GB',
					'available': '0 GB',
					'capacity': '0 GB',
					'is_active': True
				}
			}
		}
	]
	@patch('stack.commands.list.vm.storage.pool.Hypervisor', create_autospec=True)
	@patch.object(target=Command, attribute="addOutput", autospec=True)
	@pytest.mark.parametrize('pool_info', POOL_VALUES)
	def test_list_vm_storage_pool_run(
		self,
		mock_addOutput,
		mock_hypervisor,
		command,
		pool_info
	):
		hypervisor = mock_hypervisor.return_value

		# Each time pool_info is called, return
		# the next pool values
		hypervisor.pool_info.side_effect =  pool_info.values()

		# Assume every host is a valid hypervisor for
		# this test
		command.is_hypervisor = lambda h: True

		command.run((), pool_info.keys())
		actual_addOutput_calls = mock_addOutput.call_args_list

		# For each hypervisor called, check the pool
		# output matches what we expect
		for hypervisor_name, pools in pool_info.items():

			# Check the hypervisor kvm conn object
			# was called for the correct host
			mock_hypervisor.assert_any_call(hypervisor_name)
			for pool_name, pool_val in pools.items():

				# Check we got the right pool information
				hypervisor.pool_info.called_with(pool_name)

				# Make sure addOutput was called with
				# the correct values
				assert call(ANY, owner=hypervisor_name, vals=[pool_name, *pool_val.values()]) in actual_addOutput_calls

	def test_list_vm_storage_pool_no_hypervisors(self, command):

		# No hosts are valid hypervisors
		command.is_hypervisor = lambda h: False
		command.colors = ''

		with pytest.raises(ArgError, match='error - "hypervisor" argument f is not a valid hypervisor\n'):
			command.run((), 'foo')

	@patch('stack.commands.list.vm.storage.pool.Hypervisor', create_autospec=True)
	def test_list_vm_storage_pool_params(
		self,
		mock_hypervisor,
		command
	):
		command.is_hypervisor = lambda h: True

		# Force fillParams to be the pool
		# parameter value
		command.fillParams = lambda p: ('foo', )
		hypervisor = mock_hypervisor.return_value
		command.run(('foo', ), ['hypervisor-foo'])

		# Only the pool given as a param should be called
		mock_hypervisor.assert_called_once_with('hypervisor-foo')
		hypervisor.pool_info.assert_called_once_with(filter_pool='foo')
