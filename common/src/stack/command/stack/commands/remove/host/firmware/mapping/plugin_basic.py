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
from stack.exception import ArgError, ParamError, ParamRequired, CommandError

class Plugin(stack.commands.Plugin):
	"""Attempts to remove firmware mappings based on the provided arguments."""

	def provides(self):
		return "basic"

	def validate_make(self, make):
		"""If the make is provided, ensure it exists."""
		if make:
			# ensure the make exists
			self.owner.ensure_make_exists(make = make)

	def validate_model(self, make, model):
		"""If the model is provided, ensure the make and model exist."""
		if model:
			# ensure the model exists
			self.owner.ensure_model_exists(make = make, model = model)

	def get_firmware_mappings_to_remove(self, hosts, versions, make, model):
		"""Gets the mappings to remove using the provided arguments as a filter."""
		# If specific hosts are specified, build the query based on host.
		if hosts:
			query = """
				firmware_mapping.id
				FROM firmware_mapping
					INNER JOIN nodes
						ON firmware_mapping.node_id = nodes.ID
					INNER JOIN firmware
						ON firmware_mapping.firmware_id = firmware.id
					INNER JOIN firmware_model
						ON firmware.model_id = firmware_model.id
					INNER JOIN firmware_make
						ON firmware_model.make_id = firmware_make.id
					WHERE nodes.Name IN %s {}
			"""
			query_params = [hosts]
			# If versions and hosts are specified, get the specific mappings to remove for the hosts
			if versions:
				query = query.format(
					"AND firmware.version IN %s AND firmware_make.name=%s AND firmware_model.name=%s",
				)
				query_params.extend((versions, make, model))
			# Else if make, model, and hosts are specified, remove all mappings for that make and model for the specified hosts
			elif make and model:
				query = query.format("AND firmware_make.name=%s AND firmware_model.name=%s")
				query_params.extend((make, model))
			# Else if make and hosts are specified, remove all mappings for that make for the specified hosts.
			elif make:
				query = query.format("AND firmware_make.name=%s")
				query_params.extend((make,))
			# Else only hosts are specified, so remove all firmware mappings from the specified hosts
			else:
				query = query.format("")
		# If no hosts are specified, build the query based solely on the other params.
		else:
			query = """
				firmware_mapping.id
				FROM firmware_mapping
					INNER JOIN firmware
						ON firmware_mapping.firmware_id = firmware.id
					INNER JOIN firmware_model
						ON firmware.model_id = firmware_model.id
					INNER JOIN firmware_make
						ON firmware_model.make_id = firmware_make.id
					{}
			"""
			query_params = []
			# If versions are specified, get all mappings for the specified firmware versions.
			if versions:
				query = query.format("WHERE firmware.version IN %s AND firmware_make.name=%s AND firmware_model.name=%s")
				query_params.extend((versions, make, model))
			# Else if make and model are specified, remove all mappings for that make and model for all hosts
			elif make and model:
				query = query.format("WHERE firmware_make.name=%s AND firmware_model.name=%s")
				query_params.extend((make, model))
			# Else if make is specified, remove all mappings for that make for all hosts.
			elif make:
				query = query.format("WHERE firmware_make.name=%s")
				query_params.extend((make,))
			# otherwise remove all mappings
			else:
				query = "firmware_mapping.id FROM firmware_mapping"

		return [row[0] for row in self.owner.db.select(query, query_params)]

	def run(self, args):
		params, args = args
		hosts = tuple(unique_everseen(lowered(args)))
		# process hosts if present
		if hosts:
			# hosts must exist
			hosts = self.owner.getHosts(args = hosts)

		make, model, versions = lowered(
			self.owner.fillParams(
				names = [
					("make", ""),
					("model", ""),
					("versions", ""),
				],
				params = params,
			),
		)
		# process make if present
		self.validate_make(make = make)
		# process model if present
		self.validate_model(make = make, model = model)
		# Process versions if present
		if versions:
			# turn a comma separated string into a list of versions and
			# get rid of any duplicate names
			versions = tuple(
				unique_everseen(
					(version.strip() for version in versions.split(",") if version.strip())
				)
			)
			# ensure the versions exist
			self.owner.ensure_firmwares_exist(make = make, model = model, versions = versions)

		mappings_to_remove = self.get_firmware_mappings_to_remove(
			hosts = hosts,
			versions = versions,
			make = make,
			model = model,
		)

		# remove the mappings
		if mappings_to_remove:
			self.owner.db.execute("DELETE FROM firmware_mapping WHERE id IN %s", (mappings_to_remove,))
