import json
from pathlib import Path
import pytest

SCOPES = ("global", "host", "environment", "os", "appliance")

# Need this because load can touch filesystem files.
@pytest.mark.usefixtures("revert_etc")
class TestLoad:
	"""A test case to hold all the tests for `stack load`"""

	@pytest.mark.parametrize("scope", SCOPES)
	def test_load_processing_attr(self, host, stack_load, test_file, scope):
		"""Test that load added expected attr values at every scope."""
		# get the file path to use in load.
		file_path = Path(test_file("load/json/attr.json")).resolve(strict = True)

		# Load all of the test data into the database. Some commands output have the potential to fail,
		# such as removing existing storage partitions before loading new ones, and that is OK.
		result = stack_load(file_path)

		# Run the list command to get the results for the global scope.
		result = host.run(f"stack list {scope if scope != 'global' else ''} attr output-format=json")
		assert result.rc == 0
		listed_results = json.loads(result.stdout)

		# Load the expected result.
		expected_result = json.loads(Path(test_file(f"load/json/expected_attr_{scope}.json")).read_text())
		# Since scope collapsing can cause more objects to be listed for a scope than was set at that scope,
		# we just look for the entry we expect to be in the list an call that a success.
		assert any(
			listed_result == expected_result
			for listed_result in listed_results
		), f"Missing expected attribute {expected_result} at {scope} scope.\n\nListed attributes were:\n\n{listed_results}"

	@pytest.mark.parametrize("scope", SCOPES)
	def test_load_processing_controller(self, host, stack_load, test_file, scope):
		"""Test that load added expected storage controller values at every scope."""
		# get the file path to use in load.
		file_path = Path(test_file("load/json/controller.json")).resolve(strict = True)

		# Load all of the test data into the database. Some commands output have the potential to fail,
		# such as removing existing storage partitions before loading new ones, and that is OK.
		result = stack_load(file_path)

		# Run the list command to get the results for the global scope.
		result = host.run(f"stack list {scope if scope != 'global' else ''} storage controller output-format=json")
		assert result.rc == 0
		listed_results = json.loads(result.stdout)

		# Load the expected result.
		expected_result = json.loads(Path(test_file(f"load/json/expected_controller_{scope}.json")).read_text())
		# Since scope collapsing can cause more objects to be listed for a scope than was set at that scope,
		# we just look for the entry we expect to be in the list an call that a success.
		assert any(
			listed_result == expected_result
			for listed_result in listed_results
		), f"Missing expected storage controller {expected_result} at {scope} scope.\n\nListed storage controllers were:\n\n{listed_results}"

	@pytest.mark.parametrize("scope", SCOPES)
	def test_load_processing_firewall(self, host, stack_load, test_file, scope):
		"""Test that load added expected firewall values at every scope."""
		# get the file path to use in load.
		file_path = Path(test_file("load/json/firewall.json")).resolve(strict = True)

		# Load all of the test data into the database. Some commands output have the potential to fail,
		# such as removing existing storage partitions before loading new ones, and that is OK.
		result = stack_load(file_path)

		# Run the list command to get the results for the global scope.
		result = host.run(f"stack list {scope if scope != 'global' else ''} firewall output-format=json")
		assert result.rc == 0
		listed_results = json.loads(result.stdout)

		# Load the expected result.
		expected_result = json.loads(Path(test_file(f"load/json/expected_firewall_{scope}.json")).read_text())
		# Since scope collapsing can cause more objects to be listed for a scope than was set at that scope,
		# we just look for the entry we expect to be in the list an call that a success.
		assert any(
			listed_result == expected_result
			for listed_result in listed_results
		), f"Missing expected firewall {expected_result} at {scope} scope.\n\nListed firewalls were:\n\n{listed_results}"

	@pytest.mark.parametrize("scope", SCOPES)
	def test_load_processing_partition(self, host, stack_load, test_file, scope):
		"""Test that load added expected storage partition values at every scope."""
		# get the file path to use in load.
		file_path = Path(test_file("load/json/partition.json")).resolve(strict = True)

		# Load all of the test data into the database. Some commands output have the potential to fail,
		# such as removing existing storage partitions before loading new ones, and that is OK.
		result = stack_load(file_path)

		# Run the list command to get the results for the global scope.
		result = host.run(f"stack list {scope if scope != 'global' else ''} storage partition output-format=json")
		assert result.rc == 0
		listed_results = json.loads(result.stdout)

		# Load the expected result.
		expected_result = json.loads(Path(test_file(f"load/json/expected_partition_{scope}.json")).read_text())
		# Since scope collapsing can cause more objects to be listed for a scope than was set at that scope,
		# we just look for the entry we expect to be in the list an call that a success.
		assert any(
			listed_result == expected_result
			for listed_result in listed_results
		), f"Missing expected storage partition {expected_result} at {scope} scope.\n\nListed storage partitions were:\n\n{listed_results}"

	@pytest.mark.parametrize("scope", SCOPES)
	def test_load_processing_route(self, host, stack_load, test_file, scope):
		"""Test that load added expected route values at every scope."""
		# get the file path to use in load.
		file_path = Path(test_file("load/json/route.json")).resolve(strict = True)

		# Load all of the test data into the database. Some commands output have the potential to fail,
		# such as removing existing storage partitions before loading new ones, and that is OK.
		result = stack_load(file_path)

		# Run the list command to get the results for the global scope.
		result = host.run(f"stack list {scope if scope != 'global' else ''} route output-format=json")
		assert result.rc == 0
		listed_results = json.loads(result.stdout)

		# Load the expected result.
		expected_result = json.loads(Path(test_file(f"load/json/expected_route_{scope}.json")).read_text())
		# Since scope collapsing can cause more objects to be listed for a scope than was set at that scope,
		# we just look for the entry we expect to be in the list an call that a success.
		assert any(
			listed_result == expected_result
			for listed_result in listed_results
		), f"Missing expected route {expected_result} at {scope} scope.\n\nListed storage routes were:\n\n{listed_results}"

	@pytest.mark.parametrize("scope", SCOPES)
	def test_load_multiple_partitions(self, host, stack_load, test_file, scope):
		"""Ensure that loading partitions twice removes the previously set partitioning at that scope before adding the new partitioning."""
		# get the file path to use in load.
		real_partition_file_path = Path(test_file("load/json/partition.json")).resolve(strict = True)
		secondary_partition_file_path = Path(test_file("load/json/partition2.json")).resolve(strict = True)

		# Load the secondary partitioning first, and then load the real partitioning
		stack_load(secondary_partition_file_path)
		result = stack_load(real_partition_file_path)

		# Run the list command to get the results for the appliance scope.
		result = host.run(f"stack list {scope if scope != 'global' else ''} storage partition output-format=json")
		assert result.rc == 0
		listed_results = json.loads(result.stdout)

		# Load the expected result.
		expected_result = json.loads(Path(test_file(f"load/json/expected_partition_{scope}.json")).read_text())
		# Since scope collapsing can cause more objects to be listed for a scope than was set at that scope,
		# we just look for the entry we expect to be in the list an call that a success.
		assert any(
			listed_result == expected_result
			for listed_result in listed_results
		), f"Missing expected storage partition {expected_result} at {scope} scope.\n\nListed storage partitions were:\n\n{listed_results}"
