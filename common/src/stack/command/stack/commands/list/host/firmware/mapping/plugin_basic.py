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
from stack.util import unique_everseen
from stack.exception import ParamError

class Plugin(stack.commands.Plugin):
	"""Lists firmware mappings and filters the results on any provided arguments."""

	def provides(self):
		return "basic"

	def get_firmware_mappings(self, hosts, versions, make, model, sort):
		"""Gets the mappings using the provided arguments as a filter."""
		where_clause = []
		query_args = []

		if hosts:
			where_clause.append("nodes.Name IN %s")
			query_args.append(hosts)

		if make:
			where_clause.append("firmware_make.name=%s")
			query_args.append(make)

		if model:
			where_clause.append("firmware_model.name=%s")
			query_args.append(model)

		if versions:
			where_clause.append("firmware.version IN %s")
			query_args.append(versions)

		if where_clause:
			where_clause = f"WHERE {' AND '.join(where_clause)}"
		else:
			where_clause = ""

		return [
			(row[0], row[1:]) for row in self.owner.db.select(
				f"""
				nodes.Name, firmware.version, firmware_make.name, firmware_model.name
				FROM firmware_mapping
					INNER JOIN nodes
						ON firmware_mapping.node_id = nodes.ID
					INNER JOIN firmware
						ON firmware_mapping.firmware_id = firmware.id
					INNER JOIN firmware_model
						ON firmware.model_id = firmware_model.id
					INNER JOIN firmware_make
						ON firmware_model.make_id = firmware_make.id
				{where_clause}
				ORDER BY {sort}
				""",
				query_args,
			)
		]

	def run(self, args):
		params, hosts = args
		make, model, versions, sort, = self.owner.fillParams(
			names = [
				("make", ""),
				("model", ""),
				("versions", ""),
				("sort", "host"),
			],
			params = params,
		)

		sort_map = {
			"host": "nodes.Name",
			"make": "firmware_make.name",
			"model": "firmware_model.name",
			"version": "firmware.version",
		}
		# sort must be one of the allowed values
		try:
			# also convert to the column name for use in ORDER BY
			sort = sort_map[sort]
		except KeyError:
			raise ParamError(
				cmd = self.owner,
				param = "sort",
				msg = f"Sort must be one of: {list(sort_map.keys())}",
			)
		# process hosts if present
		if hosts:
			# hosts must exist
			hosts = self.owner.getHosts(args = hosts)

		# Process versions if present. This will check the make and model as well since those are
		# now required.
		if versions:
			# turn a comma separated string into a list of versions and
			# get rid of any duplicate names
			versions = tuple(
				unique_everseen(
					(version.strip() for version in versions.split(",") if version.strip())
				)
			)
			self.owner.ensure_firmwares_exist(make = make, model = model, versions = versions)
		# Process model if present. This will check the make as well since that is now required.
		elif model:
			self.owner.ensure_model_exists(make = make, model = model)
		# Process make if present.
		elif make:
			self.owner.ensure_make_exists(make = make)

		results = self.get_firmware_mappings(
			hosts = hosts,
			make = make,
			model = model,
			versions = versions,
			sort = sort,
		)

		# return the results
		return {
			"keys": ["host", "version", "make", "model"],
			"values": results
		}
