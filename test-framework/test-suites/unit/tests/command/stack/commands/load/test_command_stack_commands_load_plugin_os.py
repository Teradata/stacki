import json
from pathlib import Path
from unittest.mock import create_autospec
from stack.commands.load import command
from stack.commands.load.plugin_os import Plugin

class PluginUnderTest(Plugin):
	"""A subclass of the stack load OS plugin that replaces __init__ to remove the database dependency."""

	def __init__(self, *args, **kwargs):
		"""Set owner to a mock representation of the command."""
		self.owner = create_autospec(
			spec = command,
			spec_set = True,
			instance = True
		)

def test_provides():
	"""Test that provides returns the expected value."""
	assert PluginUnderTest().provides() == "os"

def test_run(test_file):
	"""Test that run performs the expected operations."""
	dump_json_section = json.loads(Path(test_file("load/os.json")).read_text())

	test_plugin = PluginUnderTest()
	test_plugin.run(section = dump_json_section)

	# Make sure the scope was set correctly.
	test_plugin.owner.set_scope.assert_called_once_with("os")

	# There's no stack commands to call to add the OS, so ensure it wasn't called.
	test_plugin.owner.stack.assert_not_called()

	# Make sure each entry was loaded correctly
	for os in dump_json_section:
		name = os.get("name")
		test_plugin.owner.load_attr.assert_any_call(os.get("attr"), name)
		test_plugin.owner.load_controller.assert_any_call(os.get("controller"), name)
		test_plugin.owner.load_partition.assert_any_call(os.get("partition"), name)
		test_plugin.owner.load_firewall.assert_any_call(os.get("firewall"), name)
		test_plugin.owner.load_route.assert_any_call(os.get("route"), name)
