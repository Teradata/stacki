# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from pathlib import Path
import stack.commands

class Command(stack.commands.sync.host.command):
	"""
	Syncs firmware to hosts that are compatible with the firmware

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero or more hosts to sync. If none are specified, all hosts will have their firmware synced.
	</arg>

	<example cmd='sync host firmware switch-18-11>
	If a compatible firmware version is tracked by stacki, the firmware will be synced to switch-18-11.
	</example>

	<example cmd='sync host firmware'>
	For each host, if a compatible firmware version is tracked by stacki, it will be synced to the host.
	</example>
	"""

	def run(self, params, args):
		self.notify('Sync Host Firmware\n')
		hosts = self.getHostnames(names = args)

		# sync all firmware first to ensure consistency with the DB
		self.call(command = 'sync.firmware')

		make_attr = 'component.make'
		model_attr = 'component.model'
		version_attr = 'component.firmware_version'
		hosts_to_sync = {}
		for host in hosts:
			host_firmware_attrs = {
				key: value
				for (key, value) in self.getHostAttrDict(host = host)[host].items()
				if key in (make_attr, model_attr, version_attr)
			}
			# if make and model are not set, there's nothing to do for this host.
			if not host_firmware_attrs or not all(key in host_firmware_attrs for key in (make_attr, model_attr)):
				self.notify(f'Skipping {host} because {make_attr} and {model_attr} attributes are not both set.\n')
				continue

			# get the desired firmware version
			if version_attr in host_firmware_attrs:
				row = self.db.select(
					'''
					firmware.file
					FROM firmware
						INNER JOIN firmware_model
							ON firmware.model_id=firmware_model.id
						INNER JOIN firmware_make
							ON firmware_model.make_id=firmware_make.id
					WHERE firmware.version=%s AND firmware_make.name=%s AND firmware_model.name=%s
					''',
					(host_firmware_attrs[version_attr], host_firmware_attrs[make_attr], host_firmware_attrs[model_attr])
				)
				# if there were no results, there's no firmware file that exists for the pinned version number
				if not row:
					self.notify(
						f'Skipping {host} because pinned firmware version {host_firmware_attrs[version_attr]} for make'
						f' {host_firmware_attrs[make_attr]} and model {host_firmware_attrs[model_attr]} does not exist.\n'
					)
				else:
					hosts_to_sync[host] = {
						'file': Path(row[0][0]).resolve(strict = True),
						'firmware_attrs': host_firmware_attrs
					}

			else:
				rows = self.db.select(
					'''
					firmware.file
					FROM firmware
						INNER JOIN firmware_model
							ON firmware.model_id=firmware_model.id
						INNER JOIN firmware_make
							ON firmware_model.make_id=firmware_make.id
					WHERE firmware_make.name=%s AND firmware_model.name=%s
					''',
					(host_firmware_attrs[make_attr], host_firmware_attrs[model_attr])
				)
				# there's no firmware available
				if not rows:
					self.notify(
						f'Skipping {host} because no firmware exists for make {host_firmware_attrs[make_attr]}'
						f' and model {host_firmware_attrs[model_attr]}.\n'
					)
				# there's more than one result, thus the desired version is ambiguous
				elif len(rows) > 1:
					self.notify(
						f'Skipping {host} because multiple firmware files exist for make {host_firmware_attrs[make_attr]}'
						f' and model {host_firmware_attrs[model_attr]}. Please set {version_attr} to pin a desired firmware version.\n'
					)
				# else there's only one firmware for the make and model, so that is assumed to be the desired one
				else:
					hosts_to_sync[host] = hosts_to_sync[host] = {
						'file': Path(rows[0][0]).resolve(strict = True),
						'firmware_attrs': host_firmware_attrs
					}

		if hosts_to_sync:
			self.runPlugins(args = hosts_to_sync)
