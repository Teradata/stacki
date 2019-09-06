import json
from pathlib import Path
import pytest

# Need this because load can touch filesystem files.
@pytest.mark.usefixtures("revert_etc")
class TestLoad:
	"""A test case to hold all the tests for `stack load`"""

	@pytest.mark.parametrize(
		"dump_json, expected_results_json, list_command_template, object_name",
		(
			("load/json/partition.json", "load/json/expected_partition.json", "stack list {} storage partition output-format=json", "storage partition"),
			("load/json/firewall.json", "load/json/expected_firewall.json", "stack list {} firewall output-format=json", "firewall"),
			("load/json/controller.json", "load/json/expected_controller.json", "stack list {} storage controller output-format=json", "storage controller"),
			("load/json/attr.json", "load/json/expected_attr.json", "stack list {} attr output-format=json", "attr"),
			("load/json/route.json", "load/json/expected_route.json", "stack list {} route output-format=json", "route"),
		),
	)
	def test_load_processing(self, host, stack_load, test_file, dump_json, expected_results_json, list_command_template, object_name):
		"""Test that loading information at the various scopes works as expected."""
		# get the file path to use in load.
		file_path = Path(test_file(dump_json)).resolve(strict = True)

		# Load all of the test data into the database. We use -e to ensure we fail if a command output by load fails.
		result = stack_load(file_path)
		assert result.rc == 0

		# Now ensure the objects were added as expected at each scope.
		expected_results_per_scope = json.loads(Path(test_file(expected_results_json)).read_text())
		for scope, expected_results in expected_results_per_scope.items():
			# Run the list command to get the results for the current scope.
			result = host.run(list_command_template.format(scope if scope != "global" else ""))
			assert result.rc == 0
			# If there is no stdout, ensure that we were expecting no results.
			if not result.stdout:
				assert not expected_results, f"No {object_name}s listed at scope {scope} when the following were expected:\n\n{expected_results}"
				continue

			listed_results = json.loads(result.stdout)

			# Since scope collapsing can cause more objects to be listed for a scope than was set at that scope,
			# we just look for the entry we expect to be in the list an call that a success.
			for expected_result in expected_results:
				assert any(
					listed_result == expected_result
					for listed_result in listed_results
				), f"Missing expected {object_name} {expected_result} at scope {scope}.\n\nListed {object_name}s were:\n\n{listed_results}"
