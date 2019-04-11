# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import stack.commands
import stack.firmware

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'basic'

	def run(self, args):
		# Unpack args.
		CommonKey, CommonResult, hosts_makes_models, expanded, hashit = args

		# This plugin gets the desired firmware version, so add that column to the header.
		header = ["desired_firmware_version"]
		values = {host_make_model: [] for host_make_model in hosts_makes_models}

		# We may be called with an empty list of hosts_makes_models in the case where there are no firmware mappings.
		# If so, skip trying to get the firmware version and just return the header to append.
		if values:
			for row in self.owner.db.select(
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
						ON firmware_model.make_id = firmware_make.id
				WHERE nodes.Name IN %s
				""",
				([host_make_model.host for host_make_model in values],)
			):
				host, make, model, version = row
				# Ensure that if a version regex exists, that we check the version in the database matches.
				# Since they are optional, it could have been set after the fact and a bad version number was
				# snuck in.
				regex_obj = self.owner.try_get_version_regex(
					make = make,
					model = model,
				)
				if regex_obj and not re.search(regex_obj.regex, version, re.IGNORECASE):
					values[CommonKey(host, make, model)].append(
						f"{version} (Invalid format per the version_regex named {regex_obj.name} and will be ignored by sync unless forced)"
					)
				else:
					values[CommonKey(host, make, model)].append(version)

		# add empty values for host + make + model combos that have no results and
		# join together mutiple version results into one string for host + make + model combos with multiple results.
		for host_make_model, value in values.items():
			if not value:
				values[host_make_model].append(None)
			elif len(value) > 1:
				values[host_make_model] = ["(ambiguous, sync will ignore unless forced) " + ", ".join(value)]

		return CommonResult(header, values)
