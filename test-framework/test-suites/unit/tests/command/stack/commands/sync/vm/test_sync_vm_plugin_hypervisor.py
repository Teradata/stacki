import pytest
from unittest.mock import create_autospec, patch, call, ANY
from stack.commands import DatabaseConnection
from stack.commands.sync.vm.plugin_hypervisor import Plugin, VmException
from stack.commands.sync.vm import Command
from stack.bool import str2bool
from collections import namedtuple

class TestSyncVmHypervisor:
	def mock_vm_exception(self, *args):
		raise VmException('Oh no something went wrong!')

	@pytest.fixture
	def mock_sync_hypervisor_plugin(self):
		"""
		A fixture for mocking Plugin instances
		"""

		mock_command = create_autospec(
			spec = Command,
			instance = True
		)

		mock_command.db = create_autospec(
			spec = DatabaseConnection,
			spec_set = True,
			instance = True
		)
		return Plugin(mock_command)

	# Test various successful input to the plugin
	# returns the expected output
	# 1. Single host
	# 2. Multiple hosts with different statuses
	#    and disk types
	CONFIG_ADD = [
		(
			{'foo': {
				'virtual machine': 'foo',
				'hypervisor': 'hypervisor-foo',
				'pending deletion': 'False',
				'status': 'off'
				}
			},
			{'foo': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'False'
				}]
			}
		),
		(
			{'foo': {
					'virtual machine': 'foo',
					'hypervisor': 'hypervisor-foo',
					'pending deletion': 'False',
					'status': 'off'
					},
				 'bar': {
					'virtual machine': 'bar',
					'hypervisor': 'hypervisor-bar',
					'pending deletion': 'False',
					'status': 'off'
					},
				 'baz': {
					'virtual machine': 'baz',
					'hypervisor': 'hypervisor-baz',
					'pending deletion': 'False',
					'status': 'off'
					}
			},
			{'foo': [
						{
						'Name': 'disk1',
						'Type': 'disk',
						'Image Name': 'disk_name',
						'Location': 'loc',
						'Pending Deletion': 'False'
					}
				],
			 'bar': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'False'
			 }],
			 'baz': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'False'
				}]
			})
	]

	@patch('stack.commands.sync.vm.plugin_hypervisor.Hypervisor', autospec=True)
	def test_sync_vm_hypervisor_add_vm(
		self,
		mock_hypervisor,
		mock_sync_hypervisor_plugin
	):
		"""
		Test adding a vm to a hypervisor
		"""

		hypervisor = mock_hypervisor.return_value.__enter__.return_value

		# Mock output of report vm
		mock_vm_config = [{'col-1': 'config_file'}]
		mock_sync_hypervisor_plugin.owner.call.return_value = mock_vm_config
		output = mock_sync_hypervisor_plugin.add_vm('foo', True, 'hypervisor-foo')

		# Check add_domain was called with our mock
		# report vm return value
		hypervisor.add_domain.assert_called_once_with('config_file')
		assert output == []

	@patch('stack.commands.sync.vm.plugin_hypervisor.Hypervisor', autospec=True)
	def test_sync_vm_hypervisor_add_vm_except(
		self,
		mock_hypervisor,
		mock_sync_hypervisor_plugin
	):
		"""
		Test add_vm outputs the correct
		error message when a VmException
		is raised
		"""

		hypervisor = mock_hypervisor.return_value.__enter__.return_value

		# Raise a VmException when add_domain is called
		hypervisor.add_domain.side_effect = self.mock_vm_exception

		# Mock output of report vm
		mock_vm_config = [{'col-1': 'config_file'}]
		mock_sync_hypervisor_plugin.owner.call.return_value = mock_vm_config
		output = mock_sync_hypervisor_plugin.add_vm('foo', True, 'hypervisor-foo')

		# Check add_domain was called with our mock
		# report vm return value
		hypervisor.add_domain.assert_called_once_with('config_file')
		assert output == ['Oh no something went wrong!']

	@patch('stack.commands.sync.vm.plugin_hypervisor.Hypervisor', autospec=True)
	def test_sync_vm_hypervisor_remove_vm(
		self,
		mock_hypervisor,
		mock_sync_hypervisor_plugin
	):
		"""
		Test adding a vm to a hypervisor
		"""

		hypervisor = mock_hypervisor.return_value.__enter__.return_value
		output = mock_sync_hypervisor_plugin.remove_vm('foo', True, 'hypervisor-foo')

		# Check remove_domain was called with our mock
		# report vm return value
		hypervisor.remove_domain.assert_called_once_with('foo')
		assert output == []

	@patch('stack.commands.sync.vm.plugin_hypervisor.Hypervisor', autospec=True)
	def test_sync_vm_hypervisor_remove_vm_except(
		self,
		mock_hypervisor,
		mock_sync_hypervisor_plugin
	):
		"""
		Test remove_vm outputs the correct
		error message when a VmException
		is raised
		"""

		hypervisor = mock_hypervisor.return_value.__enter__.return_value

		# Raise a VmException when add_domain is called
		hypervisor.remove_domain.side_effect = self.mock_vm_exception

		output = mock_sync_hypervisor_plugin.remove_vm('foo', True, 'hypervisor-foo')

		# Check add_domain was called with our mock
		# report vm return value
		hypervisor.remove_domain.assert_called_once_with('foo')
		assert output == ['Oh no something went wrong!']

	arg_tuple = namedtuple('args', 'hosts disks debug sync force autostart')
	RUN_ARGS = [
		arg_tuple(
			{
				'foo': {
					'virtual machine': 'foo',
					'hypervisor': 'hypervisor-foo',
					'status': 'off',
					'pending deletion': 'False'
				}
			},
			[],
			True,
			True,
			False,
			False,
		),
		arg_tuple(
			{
				'foo': {
					'virtual machine': 'foo',
					'hypervisor': 'hypervisor-foo',
					'status': 'off',
					'pending deletion': 'True'
				},
				'bar': {
					'virtual machine': 'bar',
					'hypervisor': 'hypervisor-bar',
					'status': 'undefined',
					'pending deletion': 'False'
				},
				'baz': {
					'virtual machine': 'baz',
					'hypervisor': 'hypervisor-baz',
					'status': 'on',
					'pending deletion': 'False'
				}
			},
			[],
			True,
			True,
			False,
			True,
		),
		arg_tuple(
			{
				'foo': {
					'virtual machine': 'foo',
					'hypervisor': 'hypervisor-foo',
					'status': 'on',
					'pending deletion': 'False'
				}
			},
			[],
			True,
			True,
			True,
			False,
		)
	]
	@patch.object(Plugin, 'add_vm', autospec=True)
	@patch.object(Plugin, 'remove_vm', autospec=True)
	@pytest.mark.parametrize('args', RUN_ARGS)
	def test_sync_vm_hypervisor_run(
		self,
		mock_remove_vm,
		mock_add_vm,
		mock_sync_hypervisor_plugin,
		args
	):
		# Simulate not errors returned from
		# add_vm or remove_vm
		mock_remove_vm.return_value = ['remove error']
		mock_add_vm.return_value = ['add error']
		mock_sync_hypervisor_plugin.owner.str2bool.side_effect = str2bool

		# Run the plugin
		output = mock_sync_hypervisor_plugin.run(args)

		# For each host input check if the correct
		# functions were called for the input
		for host, values in args.hosts.items():
			delete_vm = str2bool(values['pending deletion'])

			# Used to check if the current args are called or not
			func_call = call(ANY, host, args.debug, values['hypervisor'])
			if values['status'] != 'on' or args.force:
				if values['status'] != 'undefined':
					assert func_call in mock_remove_vm.call_args_list
				if delete_vm:
					assert func_call not in mock_add_vm.call_args_list
				else:
					assert func_call in mock_add_vm.call_args_list
			else:
				assert func_call not in mock_remove_vm.call_args_list
				assert func_call not in mock_add_vm.call_args_list
		assert output == ['remove error', 'add error']
