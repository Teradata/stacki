import json
from pathlib import Path
import contextlib

def get_partitions_by_scope(dump_json, scope = "global"):
	"""Retrieve all the partitions keyed off the scopes within which they reside.

	This drills into the nested dump_json object as necessary to find all "partition" keys, and treats the
	outer context under which the "partition" key is nested as the scope. If there is no outer scope,
	the scope defaults to "global".
	"""
	partitions_by_scope = {}
	if hasattr(dump_json, "items") and callable(dump_json.items):
		# If if we're iterating something that looks like a dictionary,
		# iterate over each key value pair looking for the "partition" key.
		for key, value in dump_json.items():
			# If we found the key, add the partitions at the scope level we are currently in.
			if key == "partition":
				# Set up the list of partitions in the scope if we haven't already.
				if scope not in partitions_by_scope:
					partitions_by_scope[scope] = []

				# If we are in a scope that is not global, the partitions should be nested under some name
				# I.E. hostname, appliance name, os name, or environment name.
				if "name" in dump_json:
					# This is set like this to match the format output by stack list <scope> storage partition.
					partitions_by_scope[scope].extend(
						{scope: dump_json["name"], **partition}
						for partition in value
					)
				else:
					partitions_by_scope[scope].extend(value)

			# Otherwise, recurse into the value using the key as the new scope.
			else:
				partitions_by_scope.update(get_partitions_by_scope(dump_json = value, scope = key))
	else:
		# Otherwise, try to iterate the value if it is not a string, and try to get partitions out of each
		# element inside using the current scope as the scope.
		if not isinstance(dump_json, str):
			with contextlib.suppress(TypeError):
				# If the value is not iterable, this will raise a TypeError that we ignore using suppress on purpose,
				# meaning we skip this value.
				for item in dump_json:
					partitions_by_scope.update(get_partitions_by_scope(dump_json = item, scope = scope))

	return partitions_by_scope

def test_load_partition_processing(host, test_file):
	"""Test that loading partition information at the various scopes works as expected."""
	# load up the JSON so we can parse out what the partitioning should be
	file_path = Path(test_file('load/json/partitions.json')).resolve(strict = True)
	dump_json = json.loads(file_path.read_text())
	# Get a listing of partitions that should be added per scope based on the dump.json.
	expected_partitions_by_scope = get_partitions_by_scope(dump_json = dump_json)

	# Some commands this outputs might blow up, but what we really care about are the partitions being added.
	host.run(f"stack load {file_path} | bash -x")

	# Now ensure the partitions were added as expected at each scope.
	for scope, expected_partitions in expected_partitions_by_scope.items():
		result = host.run(f"stack list {scope if scope != 'global' else ''} storage partition output-format=json")
		assert result.rc == 0
		if not result.stdout:
			assert not expected_partitions, f"No partitions listed at scope {scope} when the following were expected: {expected_partitions}"
			continue

		listed_partitions = json.loads(result.stdout)

		# Since scope collapsing can cause more partitions to be listed for a scope than was set at that scope,
		# we just look for the entry we expect to be in the list an call that a success.
		for expected_partition in expected_partitions:
			assert any(
				listed_partition == expected_partition
				for listed_partition in listed_partitions
			), f"Missing expected partition {expected_partition} at scope {scope}."
