# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
from collections import namedtuple
import stack.commands
from stack.exception import CommandError
import stack.firmware
from stack.util import flatten

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'version'

	def requires(self):
		return ['basic']

	def check_errors(self, results):
		"""Checks for any errors in the results of run_implementations_parallel. If there are errors,
		this will aggregate them all into one CommandError and raise it.
		"""
		# drop any results that didn't have any errors and aggregate the rest into one exception
		error_messages = []
		for error in (
			value.exception for value in results.values()
			if value is not None and value.exception is not None
		):
			# if this looks like a stacki exception type, grab the message from it.
			if hasattr(error, 'message') and callable(getattr(error, 'message')):
				error_messages.append(error.message())
			else:
				error_messages.append(f'{error}')

		if error_messages:
			error_message = '\n'.join(error_messages)
			raise CommandError(
				cmd = self.owner,
				msg = f"Errors occurred while listing firmware:\n{error_message}"
			)

	def run(self, args):
		# Unpack args.
		CommonKey, CommonResult, hosts_makes_models, expanded, hashit = args
		hosts = [host_make_model.host for host_make_model in hosts_makes_models]
		# get all host attrs up front
		host_attrs = self.owner.getHostAttrDict(host = hosts)

		mapped_by_imp_name = {}
		# don't look in the db if here are no hosts.
		if hosts:
			for row in self.owner.db.select(
				"""
				firmware_imp.name, nodes.Name, firmware_make.name, firmware_model.name
				FROM firmware_mapping
					INNER JOIN nodes
						ON firmware_mapping.node_id = nodes.ID
					INNER JOIN firmware
						ON firmware_mapping.firmware_id = firmware.id
					INNER JOIN firmware_model
						ON firmware.model_id = firmware_model.id
					INNER JOIN firmware_make
						ON firmware_model.make_id = firmware_make.id
					INNER JOIN firmware_imp
						ON firmware_model.imp_id = firmware_imp.id
				WHERE nodes.Name IN %s
				""",
				(hosts,)
			):
				imp, host, make, model = row
				if imp in mapped_by_imp_name:
					mapped_by_imp_name[imp].update({CommonKey(host, make, model): host_attrs[host]})
				else:
					mapped_by_imp_name[imp] = {CommonKey(host, make, model): host_attrs[host]}

		# run the implementations in parallel.
		results_by_imp = self.owner.run_implementations_parallel(
			implementation_mapping = mapped_by_imp_name,
			display_progress = True,
		)
		# Check for any errors. This will raise an exception if any implementations raised an exception.
		self.check_errors(results = results_by_imp)
		# rebuild the results as (host, make, model) mapped to version
		results_by_host_make_model = {
			host_make_model: version for host_make_model, version in flatten(
				results.result.items() for results in results_by_imp.values()
				if results is not None and results.result is not None
			)
		}

		# Use the version_regex (if set) to parse out and validate the version numbers returned by the implementations
		for host_make_model, version in results_by_host_make_model.items():
			regex_obj = self.owner.try_get_version_regex(
				make = host_make_model.make,
				model = host_make_model.model,
			)
			if regex_obj:
				match = re.search(regex_obj.regex, version, re.IGNORECASE)
				if not match:
					results_by_host_make_model[host_make_model] = f"{version} (Doesn't validate using the version_regex named {regex_obj.name} and will be ignored by sync)"
				else:
					results_by_host_make_model[host_make_model] = match.group()

		# Do a final pass to turn the results into a list as the top level command expects.
		# Also set None for host + make + model combos that had no results.
		for host_make_model in hosts_makes_models:
			if host_make_model not in results_by_host_make_model:
				results_by_host_make_model[host_make_model] = [None]
			else:
				results_by_host_make_model[host_make_model] = [results_by_host_make_model[host_make_model]]

		return CommonResult(header = ['current_firmware_version'], values = results_by_host_make_model)
