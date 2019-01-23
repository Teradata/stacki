# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError
import stack.firmware

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
		for error in [
			value['exception'] for value in results.values()
			if value is not None and value['exception'] is not None
		]:
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

	def run_make(self, hosts, host_attrs):
		"""Try to run the make implementation for all provided hosts in parallel and gather the results.

		This will raise a CommandError if any of the implementations raised exceptions. The error messages
		from the implementations will be aggregated into the CommandError raised.
		"""
		mapped_by_imp_name = {
			f'{host_attrs[host][stack.firmware.MAKE_ATTR]}': {}
			for host in hosts
		}
		for host in hosts:
			mapped_by_imp_name[f'{host_attrs[host][stack.firmware.MAKE_ATTR]}'].update(
				{host: host_attrs[host]}
			)
		# get results and check for any errors
		results = self.owner.run_implementations_parallel(
			implementation_mapping = mapped_by_imp_name,
			display_progress = True,
		)
		self.check_errors(results = results)

		return results

	def run_make_model(self, hosts, host_attrs):
		"""Try to run the make + model implementation for all provided hosts in parallel and gather the results.

		This will raise a CommandError if any of the implementations raised exceptions. The error messages
		from the implementations will be aggregated into the CommandError raised.
		"""
		mapped_by_imp_name = {
			f'{host_attrs[host][stack.firmware.MAKE_ATTR]}_{host_attrs[host][stack.firmware.MODEL_ATTR]}': {}
			for host in hosts
		}
		for host in hosts:
			mapped_by_imp_name[
				f'{host_attrs[host][stack.firmware.MAKE_ATTR]}_{host_attrs[host][stack.firmware.MODEL_ATTR]}'
			].update({host: host_attrs[host]})
		# get results and check for any errors
		results = self.owner.run_implementations_parallel(
			implementation_mapping = mapped_by_imp_name,
			display_progress = True,
		)
		self.check_errors(results = results)

		return results

	def run(self, args):
		hosts, expanded, hashit = args

		host_results = {host: [] for host in hosts}
		# get all host attrs up front
		host_attrs = self.owner.getHostAttrDict(host = hosts)

		# get hosts with attributes set, and set no results for those missing required attributes
		hosts_to_check = []
		for host in hosts:
			if all(
				key in host_attrs[host] for key in (stack.firmware.MAKE_ATTR, stack.firmware.MODEL_ATTR)
			):
				hosts_to_check.append(host)
			# if make and model are not set, there's nothing to look up.
			else:
				host_results[host].append(None)

		# run the more specific make + model implementations first as we prefer those results over the more
		# generic make only implementation. This will raise an exception if any implementations raised an
		# exception.
		make_model_results_by_imp = self.run_make_model(hosts = hosts_to_check, host_attrs = host_attrs)
		remaining_hosts_to_check = [
			host for host, version in (
				result.items() for result, exception in (
					results.items() for implementation, results in make_model_results_by_imp.items()
					if results is not None
				) if result is not None
			) if version is None
		]
		# run the more generic make implementation for the remaining hosts. This will raise an exception if
		# any implementations raised an exception.
		make_results_by_imp = self.run_model(hosts = remaining_hosts_to_check, host_attrs = host_attrs)

		host_results[host].append(current_version)

		return {'keys': ['current firmware version'], 'values': host_results}
