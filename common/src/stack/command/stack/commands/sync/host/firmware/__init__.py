# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from pathlib import Path
import stack.commands
import stack.firmware
from stack.commands.argument_processors import FirmwareArgumentProcessor

class Command(stack.commands.sync.host.command, FirmwareArgumentProcessor):
	"""
	Syncs firmware to hosts that are compatible with the firmware

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero or more hosts to sync. If none are specified, all hosts will have their firmware synced.
	</arg>

	<param type='bool' name='force'>
	Force the firmware update process to run for hosts that are already in sync.
	</param>

	<example cmd='sync host firmware switch-18-11>
	If a compatible firmware version is tracked by stacki, the firmware will be synced to switch-18-11.
	</example>

	<example cmd='sync host firmware'>
	For each host, if a compatible firmware version is tracked by stacki, it will be synced to the host.
	</example>
	"""

	def get_hosts_to_sync(self, hosts):
		"""Returns a dictionary keyed off of the hosts that are able to be synced based on their attributes
		and the firmware data in the database.
		"""
		hosts_to_sync = {}
		for host in hosts:
			host_firmware_attrs = {
				key: value
				for (key, value) in self.getHostAttrDict(host = host)[host].items()
				if key in (stack.firmware.MAKE_ATTR, stack.firmware.MODEL_ATTR, stack.firmware.FIRMWARE_ATTR)
			}
			# if make and model are not set, there's nothing to do for this host.
			if not host_firmware_attrs or not all(
				key in host_firmware_attrs
				for key in (stack.firmware.MAKE_ATTR, stack.firmware.MODEL_ATTR)
			):
				self.notify(
					f'Skipping {host} because {stack.firmware.MAKE_ATTR} and'
					f' {stack.firmware.MODEL_ATTR} attributes are not both set.'
				)
				continue

			# get the desired firmware version
			if stack.firmware.FIRMWARE_ATTR in host_firmware_attrs:
				row = self.db.select(
					'''
					firmware.file, firmware.version
					FROM firmware
						INNER JOIN firmware_model
							ON firmware.model_id=firmware_model.id
						INNER JOIN firmware_make
							ON firmware_model.make_id=firmware_make.id
					WHERE firmware.version=%s AND firmware_make.name=%s AND firmware_model.name=%s
					''',
					(
						host_firmware_attrs[stack.firmware.FIRMWARE_ATTR],
						host_firmware_attrs[stack.firmware.MAKE_ATTR],
						host_firmware_attrs[stack.firmware.MODEL_ATTR],
					)
				)
				# if there were no results, there's no firmware file that exists for the pinned version number
				if not row:
					self.notify(
						f'Skipping {host} because pinned firmware version'
						f' {host_firmware_attrs[stack.firmware.FIRMWARE_ATTR]} for make'
						f' {host_firmware_attrs[stack.firmware.MAKE_ATTR]} and model'
						f' {host_firmware_attrs[stack.firmware.MODEL_ATTR]} does not exist.'
					)
				else:
					hosts_to_sync[host] = {
						'file': Path(row[0][0]).resolve(strict = True),
						'version': row[0][1],
						'firmware_attrs': host_firmware_attrs,
					}

			else:
				rows = self.db.select(
					'''
					firmware.file, firmware.version
					FROM firmware
						INNER JOIN firmware_model
							ON firmware.model_id=firmware_model.id
						INNER JOIN firmware_make
							ON firmware_model.make_id=firmware_make.id
					WHERE firmware_make.name=%s AND firmware_model.name=%s
					''',
					(host_firmware_attrs[stack.firmware.MAKE_ATTR], host_firmware_attrs[stack.firmware.MODEL_ATTR])
				)
				# there's no firmware available
				if not rows:
					self.notify(
						f'Skipping {host} because no firmware exists for make'
						f' {host_firmware_attrs[stack.firmware.MAKE_ATTR]}'
						f' and model {host_firmware_attrs[stack.firmware.MODEL_ATTR]}.'
					)
				# there's more than one result, thus the desired version is ambiguous
				elif len(rows) > 1:
					self.notify(
						f'Skipping {host} because multiple firmware files exist'
						f' for make {host_firmware_attrs[stack.firmware.MAKE_ATTR]} and model'
						f' {host_firmware_attrs[stack.firmware.MODEL_ATTR]}. Please set'
						f' {stack.firmware.FIRMWARE_ATTR} to pin a desired firmware version.'
					)
				# else there's only one firmware for the make and model, so that is assumed to be the desired one
				else:
					hosts_to_sync[host] = {
						'file': Path(rows[0][0]).resolve(strict = True),
						'version': rows[0][1],
						'firmware_attrs': host_firmware_attrs
					}

		return hosts_to_sync

	def run(self, params, args):
		self.notify('Sync Host Firmware')
		hosts = self.getHostnames(names = args)
		force, = self.fillParams(
			names = [('force', False)],
			params = params
		)
		force = self.str2bool(force)

		# sync all firmware first to ensure consistency with the DB
		self.call(command = 'sync.firmware')
		# reduce to the hosts we can sync and process them.
		hosts_to_sync = self.get_hosts_to_sync(hosts = hosts)
		if hosts_to_sync:
			# grab all the current firmware versions
			current_firmware_versions = {
				result['host']: result['current firmware version']
				for result in self.call(command = 'list.host.firmware', args = list(hosts_to_sync.keys()))
			}
			# we need to check for hosts that already have the current version if force is not specified
			if not force:
				# get the hosts to skip
				hosts_to_skip = []
				for host, value in hosts_to_sync.items():
					desired = value['version']
					current = current_firmware_versions[host]
					if desired == current:
						self.notify(f"Skipping {host} because the current version {current} matches the desired version {desired}")
						hosts_to_skip.append(host)

				# remove them from the hosts to sync
				for host in hosts_to_skip:
					hosts_to_sync.pop(host)

			# add the current version information
			for host, value in hosts_to_sync.items():
				value['current_firmware_version'] = current_firmware_versions[host]

			self.runPlugins(args = hosts_to_sync)
