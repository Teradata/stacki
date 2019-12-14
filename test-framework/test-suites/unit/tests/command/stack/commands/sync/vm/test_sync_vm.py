import pytest
from unittest.mock import create_autospec, patch, call, ANY
from stack.commands.sync.vm import Command
from stack.bool import str2bool
from collections import namedtuple

class TestSyncVm:
	def mock_vm_exception(self, *args, **kwargs):
		raise VmException('Oh no something went wrong!')

	class CommandUnderTest(Command):
		"""
		A class derived from the Command class under test used to override __init__.
		This allows easier instantiation for testing purposes by excluding the base Command
		class initialization code.
		"""
		def __init__(self):
			pass

	@pytest.fixture
	def command(self):
		"""
		Fixture to create and return a Command class instance for testing.
		"""
		return self.CommandUnderTest()

	def run_call_return(self, vm_hosts, vm_disks, *args, **kwargs):
		"""
		Return the input hosts and disks
		depending ont he input args
		"""

		if 'list.vm' in args:
			return vm_hosts
		elif 'list.vm.storage' in args:
			return vm_disks

	param_fields = ['debug', 'hypervisor', 'force', 'autostart', 'sync_ssh']
	params = namedtuple(
			'params',
			param_fields,
			defaults=(False, '', False, False, True)
		)

	# Test various input to sync vm:
	# 1. A single VM that is off
	# 2. Several VM's with different
	# 	 states
	# 3. A single VM that is on with
	#	 the force and debug
	#    parameter enabled
	SYNC_VM_INPUT = [
		(
			('foo', ),
			params(),
			[
				{
					'virtual machine': 'foo',
					'status': 'off'
				}
			],
			[
				{
					'Virtual Machine': 'foo'
				}
			],
			{
				'foo':
				{
					'virtual machine': 'foo',
					'status': 'off'
				}
			},
			{ 'foo':
				[{
					'Virtual Machine': 'foo'
				}]
			}
		),
		(
			('foo', 'bar', 'baz'),
			params(hypervisor='hypervisor-foo'),
			[
				{
					'virtual machine': 'foo',
					'status': 'off'
				},
				{
					'virtual machine': 'bar',
					'status': 'on'
				},
				{
					'virtual machine': 'baz',
					'status': 'undefined'
				}
			],
			[
				{
					'Virtual Machine': 'foo'
				},
				{
					'Virtual Machine': 'baz'
				}
			],
			{
				'foo':
				{
					'virtual machine': 'foo',
					'status': 'off'
				},
				'baz':
				{
					'virtual machine': 'baz',
					'status': 'undefined'
				}
			},
			{
				'foo':
					[{
						'Virtual Machine': 'foo'
					}],
				'baz':
					[{
						'Virtual Machine': 'baz'
					}]
			}
		),
		(
			('foo', ),
			params(hypervisor='hypervisor-foo', force=True, debug=True),
			[
				{
					'virtual machine': 'foo',
					'status': 'on'
				}
			],
			[
				{
					'Virtual Machine': 'foo'
				}
			],
			{
				'foo':
				{
					'virtual machine': 'foo',
					'status': 'off'
				}
			},
			{
				'foo':
				 [
					{
						'Virtual Machine': 'foo'
					}
				]
			},
		)
	]
	@patch.object(Command, 'call', autospec=True)
	@patch.object(Command, 'runPlugins', autospec=True)
	@patch.object(Command, 'fillParams', autospec=True)
	@pytest.mark.parametrize('args, params, vm_hosts, vm_disks, expect_hosts, expect_disks', SYNC_VM_INPUT)
	def test_sync_vm_run(
		self,
		mock_fill_params,
		mock_run_plugins,
		mock_call,
		command,
		args,
		params,
		vm_hosts,
		vm_disks,
		expect_hosts,
		expect_disks
	):
		"""
		Test that inputs to the Sync VM
		command calls plugins with the
		expected input arguments
		"""

		expect_plugin_args = (expect_hosts, expect_disks, params.debug, params.sync_ssh, params.force, params.autostart)
		mock_call.side_effect = lambda *args, **kwargs: self.run_call_return(vm_hosts, vm_disks, *args, **kwargs)
		mock_fill_params.return_value = params
		command.run(params, args)
		mock_run_plugins.assert_called_once_with(ANY, expect_plugin_args)

	@patch.object(Command, 'call', autospec=True)
	@patch.object(Command, 'runPlugins', autospec=True)
	@patch.object(Command, 'fillParams', autospec=True)
	@patch.object(Command, 'addOutput', autospec=True)
	def test_sync_vm_plugin_errors(
		self,
		mock_add_output,
		mock_fill_params,
		mock_run_plugins,
		mock_call,
		command
	):
		"""
		Test sync vm outputs
		any error messages from
		plugins
		"""

		args, params, vm_hosts, vm_disks, expect_hosts, expect_disk = self.SYNC_VM_INPUT[2]
		expect_plugins = [
			('hypervisor', ['hypervisor plugin error']),
			('storage', ['storage plugin error']),
			('config', ['config plugin error'])
		]
		expect_errors = [
			call(ANY, '', '\n'.join(['hypervisor plugin error'])),
			call(ANY, '', '\n'.join(['storage plugin error'])),
			call(ANY, '', '\n'.join(['config plugin error']))
		]
		mock_call.side_effect = lambda *args, **kwargs: self.run_call_return(vm_hosts, vm_disks, *args, **kwargs)
		mock_fill_params.return_value = params
		mock_run_plugins.return_value = expect_plugins
		command.run(params, args)
		assert mock_add_output.call_args_list == expect_errors

	@patch.object(Command, 'call', autospec=True)
	@patch.object(Command, 'fillParams', autospec=True)
	@patch.object(Command, 'runPlugins', autospec=True)
	def test_sync_vm_plugin_force_off(
		self,
		mock_run_plugins,
		mock_fill_params,
		mock_call,
		command
	):
		"""
		Test that a vm is turned off
		when force is enabled
		"""

		args = ('foo', )
		params = self.params(force=True)
		mock_fill_params.return_value = params
		vm_hosts = [{
				'virtual machine': 'foo',
				'status': 'on'
		}]
		vm_disks = [{
				'Virtual Machine': 'foo'
		}]
		mock_call.side_effect = lambda *args, **kwargs: self.run_call_return(vm_hosts, vm_disks, *args, **kwargs)
		mock_run_plugins.return_value = [('bar', 'baz')]
		command.run(params, args)
		set_power_call = call(ANY, f'set.host.power', args = ['foo', 'command=off', 'method=kvm'])
		assert set_power_call in mock_call.call_args_list
