from unittest.mock import create_autospec, ANY
import pytest
from stack.commands import DatabaseConnection
from stack.commands.list.firmware import Command
from stack.commands.list.firmware.plugin_basic import Plugin

class TestListFirmwareBasicPlugin:
	"""A test case for the list firmware imp basic plugin."""

	@pytest.fixture
	def basic_plugin(self):
		"""A fixture that returns the plugin instance for use in tests.

		This sets up the required mocks needed to construct the plugin class.
		"""
		mock_command = create_autospec(
			spec = Command,
			instance = True,
		)
		mock_command.db = create_autospec(
			spec = DatabaseConnection,
			spec_set = True,
			instance = True,
		)
		return Plugin(command = mock_command)

	def test_provides(self, basic_plugin):
		"""Ensure that provides returns 'basic'."""
		assert basic_plugin.provides() == "basic"

	def test_run(self, basic_plugin):
		"""Test that run queries the DB as expected."""
		basic_plugin.owner.db.select.return_value = [
			["foo", "bar", "baz", "fizz", "buzz", "bam!"],
			["this", "is", "a", "test", "return", "value"],
		]
		expected_results = {
			"keys": ["make", "model", "version", "source", "hash", "hash_alg"],
			"values": [(row[0], row[1:]) for row in basic_plugin.owner.db.select.return_value],
		}

		assert expected_results == basic_plugin.run(args = True)

		basic_plugin.owner.db.select.assert_called_once_with(ANY)

	def test_run_expanded_false(self, basic_plugin):
		"""Test that run queries the DB as expected when expanded is False."""
		basic_plugin.owner.db.select.return_value = [
			["foo", "bar", "baz"],
			["fizz", "buzz", "bam!"],
		]
		expected_results = {
			"keys": ["make", "model", "version"],
			"values": [(row[0], row[1:]) for row in basic_plugin.owner.db.select.return_value],
		}

		assert expected_results == basic_plugin.run(args = False)

		basic_plugin.owner.db.select.assert_called_once_with(ANY)
