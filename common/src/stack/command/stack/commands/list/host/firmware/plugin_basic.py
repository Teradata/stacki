# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'basic'

	def run(self, args):
		# Unpack args.
		CommonResult, database_values_dict = args

		# This plugin gets the desired firmware version, so add that column to the header.
		header = ["desired_firmware_version"]
		results = {host_make_model: [] for host_make_model in database_values_dict}

		# For each host_make_model + firmware_version, firmware_imp combination, get the desired firmware version and validate it.
		for host_make_model, firmware_info in database_values_dict.items():
			# Ensure that if a version regex exists, that we check the version in the database matches.
			# Since they are optional, it could have been set after the fact and a bad version number was
			# snuck in.
			regex_obj = self.owner.try_get_version_regex(
				make = host_make_model.make,
				model = host_make_model.model,
			)
			if regex_obj and not re.search(regex_obj.regex, firmware_info.firmware_version, re.IGNORECASE):
				results[host_make_model].append(
					f"{firmware_info.firmware_version} (Invalid format per the version_regex named {regex_obj.name} and will be ignored by sync unless forced)"
				)
			else:
				results[host_make_model].append(firmware_info.firmware_version)

		# add empty values for host + make + model combos that have no results and
		# join together mutiple version results into one string for host + make + model combos with multiple results.
		for host_make_model, value in results.items():
			if not value:
				results[host_make_model].append(None)
			elif len(value) > 1:
				results[host_make_model] = [f"(ambiguous, sync will ignore unless forced) {', '.join(value)}"]

		return CommonResult(header, results)
