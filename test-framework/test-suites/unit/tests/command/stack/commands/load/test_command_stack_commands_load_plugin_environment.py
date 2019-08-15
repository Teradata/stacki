import json
from pathlib import Path
from unittest.mock import create_autospec
from stack.commands.load import command
from stack.commands.load.plugin_environment import Plugin

class PluginUnderTest(Plugin):
	"""A subclass of the stack load environment plugin that replaces __init__ to remove the database dependency."""

	def __init__(self, *args, **kwargs):
		"""Set owner to a mock representation of the command."""
		self.owner = create_autospec(
			spec = command,
			spec_set = True,
			instance = True
		)

def test_provides():
	"""Test that provides returns the expected value."""
	assert PluginUnderTest().provides() == "environment"

def test_run(test_file):
	"""Test that run performs the expected operations."""
	dump_json_section = json.loads(Path(test_file("load/environment.json")).read_text())

	test_plugin = PluginUnderTest()
	test_plugin.run(section = dump_json_section)

	# Make sure the scope was set correctly.
	test_plugin.owner.set_scope.assert_called_once_with("environment")

	# Make sure each entry was loaded correctly
	for environment in dump_json_section:
		name = environment.get("name")
		test_plugin.owner.stack.assert_any_call('add.environment', name)
		test_plugin.owner.load_attr.assert_any_call(environment.get("attr"), name)
		test_plugin.owner.load_controller.assert_any_call(environment.get("controller"), name)
		test_plugin.owner.load_partition.assert_any_call(environment.get("partition"), name)
		test_plugin.owner.load_firewall.assert_any_call(environment.get("firewall"), name)
		test_plugin.owner.load_route.assert_any_call(environment.get("route"), name)
