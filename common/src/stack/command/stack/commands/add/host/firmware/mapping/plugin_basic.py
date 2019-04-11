# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.util import unique_everseen, lowered
from stack.exception import CommandError

class Plugin(stack.commands.Plugin):
	"""Attempts to map firmware versions to hosts."""

	def provides(self):
		return "basic"

	def ensure_unique_mappings(self, hosts, make, model, version):
		"""Ensure the proposed mappings are unique."""
		# The mappings must not already exist
		existing_mappings = [
			f"{host} mapped to firmware {version} for make {make} and model {model}" for host, make, model, version in (
				row for row in self.owner.db.select(
					"""
					nodes.Name, firmware_make.name, firmware_model.name, firmware.version
					FROM firmware_mapping
						INNER JOIN nodes
							ON firmware_mapping.node_id = nodes.ID
						INNER JOIN firmware
							ON firmware_mapping.firmware_id = firmware.id
						INNER JOIN firmware_model
							ON firmware.model_id = firmware_model.id
						INNER JOIN firmware_make
							ON firmware_model.make_id = firmware_model.id
					WHERE nodes.Name IN %s AND firmware_make.name = %s AND firmware_model.name = %s AND firmware.version = %s
					""",
					(hosts, make, model, version)
				)
			)
		]
		if existing_mappings:
			existing_mappings = "\n".join(existing_mappings)
			raise CommandError(cmd = self.owner, msg = f"The following firmware mappings already exist:\n{existing_mappings}")

	def run(self, args):
		params, args = args
		args = tuple(unique_everseen(lowered(args)))
		hosts = self.owner.getHosts(args = args)

		version, make, model, = lowered(
			self.owner.fillParams(
				names = [
					("version", ""),
					("make", ""),
					("model", ""),
				],
				params = params,
			)
		)
		# Make, model, and version are required. This checks them all.
		self.owner.ensure_firmware_exists(make = make, model = model, version = version)
		# Make sure the proposed mappings are unique.
		self.ensure_unique_mappings(hosts = hosts, make = make, model = model, version = version)

		# Get the ID's of all the hosts
		node_ids = (
			row[0] for row in self.owner.db.select("ID FROM nodes WHERE Name in %s", (hosts,))
		)
		# Get the firmware version ID
		firmware_id = self.owner.get_firmware_id(make = make, model = model, version = version)

		# Add the mapping entries.
		self.owner.db.execute(
			"""
			INSERT INTO firmware_mapping (
				node_id,
				firmware_id
			)
			VALUES (%s, %s)
			""",
			[(node_id, firmware_id) for node_id in node_ids],
			many = True,
		)
