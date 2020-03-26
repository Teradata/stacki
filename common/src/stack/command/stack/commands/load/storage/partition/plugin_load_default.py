# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import tempfile
import json

import stack.commands
from stack.commands import ApplianceArgProcessor, OSArgProcessor
from stack.exception import CommandError


class Plugin(ApplianceArgProcessor, OSArgProcessor, stack.commands.Plugin):
	"""
	Plugin that invokes 'stack add storage partition' and adds
	the partitions to the database.
	"""

	def provides(self):
		return 'default'

	def _add_dump_data(self, scope, target, data, dump_data):
		"""Add dump data for partition objects nested under the given scope."""
		# If the scope already has data, be sure to append it appropriately.
		if scope in dump_data:
			existing_scope_data = None
			# See if the data with the target name already exists at the scope
			for scope_data in dump_data[scope]:
				if scope_data["name"] == target:
					existing_scope_data = scope_data
					break

			# If it does, append the new data to the existing named entry.
			if existing_scope_data is not None:
				existing_scope_data["partition"].extend(data)
			# Otherwise, add a new named entry to the scope.
			else:
				dump_data[scope].append(
					{
						"name": target,
						"partition": data,
					},
				)
		# Otherwise, initialize a new list of named data within the scope.
		else:
			dump_data[scope] = [
				{
					"name": target,
					"partition": data,
				},
			]

		return dump_data

	def run(self, args):
		appliances = self.getApplianceNames()
		oses = self.getOSNames()

		# Build a dump.json like dictionary object to pass into `stack load`
		dump_data = {}

		for target, data in args.items():
			# Global just goes at the top level of the dict as a list of partition dictionaries
			if target == 'global':
				if "partition" in dump_data:
					dump_data["partition"].extend(data)
				else:
					dump_data["partition"] = data

				continue

			# Otherwise, figure out which scope the target is in.
			if target in appliances:
				scope = "appliance"
			elif target in oses:
				scope = "os"
			else:
				scope = "host"

			# Appliances, Oses, and Hosts are nested objects, with the partition list inside the appliance.
			dump_data = self._add_dump_data(
				scope = scope,
				target = target,
				data = data,
				dump_data = dump_data,
			)

		# Write to a temporary file that stack load can read
		with tempfile.NamedTemporaryFile(mode = "w") as temp_file:
			json.dump(dump_data, temp_file)
			temp_file.flush()
			self.owner.call(command = "load", args = [temp_file.name, "exec=True"])
