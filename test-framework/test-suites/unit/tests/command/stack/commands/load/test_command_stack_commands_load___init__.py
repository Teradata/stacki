from stack.commands.load import command
from stack.exception import CommandError
import pytest
from unittest.mock import patch

class CommandUnderTest(command):
	"""A subclass of the stack load command that replaces __init__ to remove the database dependency."""

	def __init__(self, *args, **kwargs):
		pass

@pytest.fixture
def partitions():
	"""Fixture to set up test partition information."""
	return [
		{
			"device": "sda",
			"partid": 5,
			"mountpoint": "/",
			"size": 1024,
			"fstype": "ext4",
			"options": "host_options",
		},
		{
			"device": "sda",
			"partid": 6,
			"mountpoint": "/var",
			"size": 0,
			"fstype": "ext4",
		},
	]

class TestLoadCommand:
	"""A test case for testing the stack load command."""

	@pytest.mark.parametrize(
		"scope, target, expected_cmd",
		(
			("global", None, "add.storage.partition"),
			("appliance", ["backend", "backend2"], "add.appliance.storage.partition"),
			("os", ["sles", "rhel"], "add.os.storage.partition"),
			("environment", ["env1", "env2"], "add.environment.storage.partition"),
			("host", ["backend-0-0", "backend-0-1"], "add.host.storage.partition"),
		)
	)
	@patch.object(target = CommandUnderTest, attribute = "stack", autospec = True)
	@patch.object(target = CommandUnderTest, attribute = "get_scope", autospec = True)
	def test_load_partition(self, mock_get_scope, mock_stack, scope, target, expected_cmd, partitions):
		# Some parameter names differ from the keys in the json, so we set up a mapping of
		# add storage partition parameter names to json key names.
		partition_keys = {
			"device": "device",
			"partid": "partid",
			"mountpoint": "mountpoint",
			"size": "size",
			"type": "fstype",
			"options": "options",
		}
		mock_get_scope.return_value = scope

		# Run the command
		test_command = CommandUnderTest()
		test_command.load_partition(partitions = partitions, target = target)

		mock_get_scope.assert_called_once_with(test_command)
		# Validate that partition commands were generated correctly.
		for partition in partitions:
			mock_stack.assert_any_call(
				test_command,
				expected_cmd,
				target,
				**{
					parameter_name: partition.get(json_key)
					for parameter_name, json_key in partition_keys.items()
				},
			)

	@pytest.mark.parametrize("test_input", (None, []))
	@patch.object(target = CommandUnderTest, attribute = "stack", autospec = True)
	@patch.object(target = CommandUnderTest, attribute = "get_scope", autospec = True)
	def test_load_partition_no_partitions(self, mock_get_scope, mock_stack, test_input):
		"""Test that load_partition early exits when there are no partitions to load."""
		CommandUnderTest().load_partition(partitions = test_input)

		mock_get_scope.assert_not_called()
		mock_stack.assert_not_called()

	@patch.object(target = CommandUnderTest, attribute = "stack", autospec = True)
	@patch.object(target = CommandUnderTest, attribute = "get_scope", autospec = True)
	def test_load_partition_non_global_scope_with_no_target(self, mock_get_scope, mock_stack, partitions):
		"""Test that load_partition raises an exception when a non-global scope is used and no target is passed."""
		mock_get_scope.return_value = "appliance"

		with pytest.raises(AssertionError):
			CommandUnderTest().load_partition(partitions = partitions)

		mock_stack.assert_not_called()

	@patch.object(target = CommandUnderTest, attribute = "call", autospec = True)
	def test__exec_commands(self, mock_call):
		"""Test that exec commands calls the requested command correctly."""
		# Set the exec_commands attribute to True
		test_command = CommandUnderTest()
		test_command.exec_commands = True

		cmd = "stack list foo"
		args = ["foo", "bar"]
		params = {"baz": "bag"}

		test_command._exec_commands(cmd = cmd, args = args, params = params)

		# Make sure the call was made correctly
		mock_call.assert_called_once_with(
			test_command,
			command = cmd,
			args = [*args, *(f"{key}={value}" for key,value in params.items())],
		)

	@patch.object(target = CommandUnderTest, attribute = "call", autospec = True)
	def test__exec_commands_suppresses_command_errors(self, mock_call):
		"""Test that command errors are suppressed when calling the stack commands."""
		# Set the exec_commands attribute to True
		test_command = CommandUnderTest()
		test_command.exec_commands = True

		cmd = "stack list foo"
		args = ["foo", "bar"]
		params = {"baz": "bag"}
		mock_call.side_effect = CommandError(msg = "foo", cmd = test_command)

		test_command._exec_commands(cmd = cmd, args = args, params = params)

	@pytest.mark.parametrize("args", (tuple(), ("foo",), ("foo", "bar")))
	@pytest.mark.parametrize(
		"params, expected_params",
		(
			({}, {}),
			({"baz": "bag"}, {"baz": "bag"}),
			({"baz": "bag", "booz": None}, {"baz": "bag"})
		),
	)
	@patch.object(target = CommandUnderTest, attribute = "_exec_commands", autospec = True)
	def test_stack(self, mock__exec_commands, args, params, expected_params):
		"""Test that stack tries to run the command if exec_commands is True."""
		# Set the exec_commands attribute to True
		test_command = CommandUnderTest()
		test_command.exec_commands = True

		cmd = "stack list foo"

		test_command.stack(cmd, *args, **params)

		# Make sure the call was made correctly
		mock__exec_commands.assert_called_once_with(
			test_command,
			cmd = cmd,
			args = args,
			params = expected_params,
		)
