from unittest.mock import patch
import pytest
from stack.commands.remove.firmware.imp import Command

class TestRemoveFirmwareImpCommand:
	"""A test case to hold the tests for the remove firmware imp stacki Command class."""

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

	@patch.object(target = Command, attribute = "runPlugins", autospec = True)
	def test_run(self, mock_runPlugins, command):
		"""Test that run will run the plugins passing through the args."""
		mock_args = ["foo", "bar", "baz"]

		command.run(params = "unused", args = mock_args)

		mock_runPlugins.assert_called_once_with(command, args = mock_args)
