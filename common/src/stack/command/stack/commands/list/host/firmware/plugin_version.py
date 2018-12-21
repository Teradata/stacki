# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'version'

	def requires(self):
		return ['basic']

	def run(self, args):
		hosts, expanded, hashit = args

		host_info = {host: [] for host in hosts}

		make_attr = 'component.make'
		model_attr = 'component.model'
		for host in hosts:
			host_firmware_attrs = {
				key: value
				for key, value in self.owner.getHostAttrDict(host = host)[host].items()
				if key in (make_attr, model_attr)
			}
			# if make and model are not set, there's nothing to look up.
			if not host_firmware_attrs or not all(key in host_firmware_attrs for key in (make_attr, model_attr)):
				host_info[host].append(None)
				continue

			# store the current version information. Prefer the more specific make + model implementation results to the
			# make implementation results.
			current_version = self.owner.runImplementation(
				name = f'{host_firmware_attrs[make_attr]}_{host_firmware_attrs[model_attr]}',
				args = host
			)
			# if we didn't get any results, run the more generic implementation
			if current_version is None:
				current_version = self.owner.runImplementation(
					name = host_firmware_attrs[make_attr],
					args = host
				)

			host_info[host].append(current_version)

		return {'keys': ['current firmware version'], 'values': host_info}
