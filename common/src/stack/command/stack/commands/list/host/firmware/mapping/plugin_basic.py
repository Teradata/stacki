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
from stack.exception import ArgError, ParamError, ParamRequired, CommandError

class Plugin(stack.commands.Plugin):
	"""Lists firmware mappings and filters the results on any provided arguments."""

	def provides(self):
		return "basic"

	def get_firmware_mappings(self, hosts, versions, make, model, sort):
		"""Gets the mappings using the provided arguments as a filter."""
		# If versions and hosts are specified, get the specific mappings for the hosts
		if versions and hosts:
			mappings = [
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
					WHERE nodes.Name IN %s AND firmware.version IN %s AND firmware_make.name=%s AND firmware_model.name=%s
					ORDER BY {sort}
					""",
					(hosts, versions, make, model)
				)
			]
		# Else if make, model, and hosts are specified, get all mappings for that make and model for the specified hosts
		elif make and model and hosts:
			mappings = [
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
					WHERE nodes.Name IN %s AND firmware_make.name=%s AND firmware_model.name=%s
					ORDER BY {sort}
					""",
					(hosts, make, model)
				)
			]
		# Else if make and hosts are specified, get all mappings for that make for the specified hosts.
		elif make and hosts:
			mappings = [
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
					WHERE nodes.Name IN %s AND firmware_make.name=%s
					ORDER BY {sort}
					""",
					(hosts, make)
				)
			]
		# Else only hosts are specified, so get all firmware mappings from the specified hosts
		elif hosts:
			mappings = [
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
					WHERE nodes.Name IN %s
					ORDER BY {sort}
					""",
					(hosts,)
				)
			]
		# Else if versions are specified, get all mappings for the specified firmware versions.
		elif versions:
			mappings = [
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
					WHERE nodes.Name IN %s AND firmware.version IN %s AND firmware_make.name=%s AND firmware_model.name=%s
					ORDER BY {sort}
					""",
					(versions, make, model)
				)
			]
		# Else if make and model are specified, get all mappings for that make and model for all hosts
		elif make and model:
			mappings = [
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
					WHERE firmware_make.name=%s AND firmware_model.name=%s
					ORDER BY {sort}
					""",
					(make, model)
				)
			]
		# Else if make is specified, get all mappings for that make for all hosts.
		elif make:
			mappings = [
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
					WHERE firmware_make.name=%s
					ORDER BY {sort}
					""",
					(make,)
				)
			]
		# otherwise get all mappings
		else:
			mappings = [
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
					ORDER BY {sort}
					"""
				)
			]

		return mappings

	def run(self, args):
		params, hosts = args
		make, model, versions, sort, = self.owner.fillParams(
			names = [
				("make", ""),
				("model", ""),
				("versions", ""),
				("sort", "host")
			],
			params = params
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
				msg = f"Sort must be one of: {list(sort_map.keys())}"
			)
		# process hosts if present
		if hosts:
			# hosts must exist
			hosts = self.owner.getHosts(args = hosts)
		# process make if present
		if make:
			# ensure the make exists
			if not self.owner.make_exists(make = make):
				raise ParamError(
					cmd = self.owner,
					param = "make",
					msg = f"The make {make} doesn't exist."
				)
		# process model if present
		if model:
			# make is now required
			if not make:
				raise ParamRequired(cmd = self.owner, param = "make")
			# ensure the model exists
			if not self.owner.model_exists(make = make, model = model):
				raise ParamError(
					cmd = self.owner,
					param = "model",
					msg = f"The model {model} doesn't exist for make {make}."
				)
		# Process versions if present
		if versions:
			# make and model are now required
			if not make:
				raise ParamRequired(cmd = self.owner, param = "make")
			if not model:
				raise ParamRequired(cmd = self.owner, param = "model")
			# turn a comma separated string into a list of versions and
			# get rid of any duplicate names
			versions = tuple(
				unique_everseen(
					(version.strip() for version in versions.split(",") if version.strip())
				)
			)
			# ensure the versions exist
			try:
				self.owner.ensure_firmwares_exist(make = make, model = model, versions = versions)
			except CommandError as exception:
				raise ArgError(
					cmd = self.owner,
					arg = "version",
					msg = exception.message()
				)

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
