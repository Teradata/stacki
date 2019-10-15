from unittest.mock import patch, call
import pytest
from stack.commands.list.firmware.make import Command

class TestListFirmwareMakeCommand:
	"""A test case to hold the tests for the list firmware make stacki Command class."""

	class CommandUnderTest(Command):
		"""A class derived from the Command class under test used to override __init__.

		This allows easier instantiation for testing purposes by excluding the base Command
		class initialization code.
		"""
		def __init__(self):
			pass

	@pytest.fixture
	def command(self):
		"""Fixture to create and return a Command class instance for testing."""
		return self.CommandUnderTest()

	@patch.object(target = Command, attribute = "str2bool", autospec = True)
	@patch.object(target = Command, attribute = "fillParams", autospec = True)
	@patch.object(target = Command, attribute = "endOutput", autospec = True)
	@patch.object(target = Command, attribute = "addOutput", autospec = True)
	@patch.object(target = Command, attribute = "beginOutput", autospec = True)
	@patch.object(target = Command, attribute = "runPlugins", autospec = True)
	def test_run(
		self,
		mock_runPlugins,
		mock_beginOutput,
		mock_addOutput,
		mock_endOutput,
		mock_fillParams,
		mock_str2bool,
		command,
	):
		"""Test that run will run the plugins, gather the results, and output them as expected."""
		mock_header = ["make", "version_regex_name"]
		mock_first_value = ("foo", ["bar"])
		mock_second_value = ("baz", ["bag"])
		mock_runPlugins.return_value = (
			(
				"basic",
				{
					"keys": mock_header,
					"values": [mock_first_value, mock_second_value],
				},
			),
		)
		mock_params = {"expanded": "True"}
		mock_fillParams.return_value = (mock_params["expanded"],)
		mock_str2bool.return_value = True

		command.run(args = "unused", params = mock_params)

		mock_fillParams.assert_called_once_with(command, names = [("expanded", False)], params = mock_params)
		mock_str2bool.assert_called_once_with(command, mock_params["expanded"])
		mock_runPlugins.assert_called_once_with(command, args = mock_str2bool.return_value)
		mock_beginOutput.assert_called_once_with(command)
		assert [
			call(command, owner = mock_first_value[0], vals = mock_first_value[1]),
			call(command, owner = mock_second_value[0], vals = mock_second_value[1]),
		] == mock_addOutput.mock_calls
		mock_endOutput.assert_called_once_with(command, header = mock_header)
