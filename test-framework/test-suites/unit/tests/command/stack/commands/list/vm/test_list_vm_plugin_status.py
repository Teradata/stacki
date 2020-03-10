import pytest
from stack.kvm import Hypervisor, VmException
from unittest.mock import create_autospec, patch, call, ANY
from stack.commands import DatabaseConnection
from stack.argument_processors.vm import VmArgumentProcessor
from stack.commands.list.vm.plugin_status import Plugin
from stack.commands.list.vm import Command

class TestListVmStatus:
	def mock_vm_exception(self, *args):
		raise VmException('Oh no something went wrong!')

	@pytest.fixture
	def mock_vm_status_plugin(self):
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

	def test_list_vm_status_no_expand(self, mock_vm_status_plugin):
		"""
		Test that the output is blank when the plugin is called
		with the expand parameter from list vm is False
		"""

		status_out = mock_vm_status_plugin.run((['foo'], False))
		assert status_out == {'keys': [], 'values': {} }


	# Test various successful input to the plugin
	# returns the expected output
	# 1. No hosts
	# 2. Single host
	# 3. Multiple hosts on different hypervisors
	# 4. Multiple hosts on the same hypervisor
	# 5. Multiple hosts where some hosts
	#    aren't defined on the hypervisor yet
	HOST_STATUS = [
		(
			[],
			[],
			[],
			{ 'keys': ['status'], 'values': {}}
		),
		(
			['foo'],
			['hypervisor-foo'],
			[{'foo': 'on'}],
			{ 'keys': ['status'], 'values': {'foo': ['on']}}
		),
		(
			['foo', 'bar', 'baz'],
			['hypervisor-foo', 'hypervisor-bar', 'hypervisor-baz'],
			[{'foo': 'on'}, {'bar': 'off'}, {'baz': 'on'}],
			{ 'keys': ['status'], 'values': {'foo': ['on'], 'bar': ['off'], 'baz': ['on']}}
		),
		(
			['foo', 'bar', 'baz'],
			['hypervisor-foo', 'hypervisor-foo', 'hypervisor-foo'],
			[{'foo': 'on'}, {'bar': 'off'}, {'baz': 'off'}],
			{ 'keys': ['status'], 'values': {'foo': ['on'], 'bar': ['off'], 'baz': ['off']}}
		),
		(
			['foo', 'bar', 'baz'],
			['hypervisor-foo', 'hypervisor-bar', 'hypervisor-baz'],
			[{'foo': 'on'}, {'bar': 'off'}, {}],
			{ 'keys': ['status'], 'values': {'foo': ['on'], 'bar': ['off'], 'baz': ['undefined']}}
		)
	]
	@patch.object(target = Plugin, attribute = 'get_hypervisor_by_name', autospec = True)
	@patch('stack.kvm.Hypervisor', autospec = True)
	@pytest.mark.parametrize('hosts, hypervisors, guest_status, expect_output', HOST_STATUS)
	def test_list_vm_status(
		self,
		mock_hypervisor,
		mock_get_hypervisor,
		mock_vm_status_plugin,
		hosts,
		hypervisors,
		guest_status,
		expect_output
	):

		# Mock outside function call
		# return values
		hypervisor = mock_hypervisor.return_value.__enter__.return_value
		hypervisor.guests.side_effect = guest_status
		mock_get_hypervisor.side_effect = hypervisors

		# Call the plugin
		actual_output = mock_vm_status_plugin.run((hosts, True))

		# Check mocked functions were called with
		# the expected args and the right amount
		# of times
		mock_get_hypervisor.assert_has_calls([call(ANY, host) for host in hosts])
		expect_args = [call(hypervisor) for hypervisor in set(hypervisors)]
		for guest_call in mock_hypervisor.call_args_list:
			assert guest_call in expect_args

	@patch.object(target = Plugin, attribute = 'get_hypervisor_by_name', autospec = True)
	@patch('stack.kvm.Hypervisor', autospec = True)
	def test_list_vm_status_exception_conn(self, mock_hypervisor, mock_get_hypervisor, mock_vm_status_plugin):
		"""
		Trigger a VmException when the status plugin
		attempts to connect to the kvm hypervisor
		"""

		mock_get_hypervisor.return_value = 'foo'

		# Raise a VmException when instantiating
		# a hypervisor object
		hypervisor = mock_hypervisor.return_value.__enter__.return_value
		hypervisor.guests.side_effect = self.mock_vm_exception

		# Call the plugin
		output = mock_vm_status_plugin.run((['bar'], True))

		# Check args
		mock_get_hypervisor.assert_called_once_with(ANY, 'bar')
		mock_hypervisor.assert_called_once_with('foo')
		expect_output = { 'keys' : ['status'], 'values': {'bar': ['Connection failed to hypervisor'] } }
		assert output == expect_output

	@patch.object(target = Plugin, attribute = 'get_hypervisor_by_name', autospec = True)
	@patch('stack.kvm.Hypervisor', autospec = True)
	def test_list_vm_status_exception_guests(self, mock_hypervisor, mock_get_hypervisor, mock_vm_status_plugin):
		"""
		Trigger a VmException exception when the status plugin
		gets the current guest status
		"""

		mock_get_hypervisor.return_value = 'foo'
		hypervisor = mock_hypervisor.return_value.__enter__.return_value

		# Raise a VmException when the
		# guests method is called
		hypervisor.guests.side_effect = self.mock_vm_exception

		# Run the plugin
		output = mock_vm_status_plugin.run((['bar'], True))

		# Check our mocked functions were called
		# with what we expect and the right amount
		# of times
		mock_get_hypervisor.assert_called_once_with(ANY, 'bar')
		mock_hypervisor.assert_called_once_with('foo')
		hypervisor.guests.assert_called_once()
		expect_output = {'keys' : ['status'], 'values': {'bar': ['Connection failed to hypervisor'] }}
		assert output == expect_output
