# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
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

	def get_host_firmware(self, host, host_attrs, host_current_firmwares, force):
		result = None
		rows = self.db.select(
			'''
			firmware.file, firmware.version, make_imp.name, model_imp.name
			FROM firmware
				INNER JOIN firmware_model
					ON firmware.model_id=firmware_model.id
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
				LEFT JOIN firmware_imp as make_imp
					ON firmware_make.imp_id = make_imp.id
				LEFT JOIN firmware_imp as model_imp
					ON firmware_model.imp_id = model_imp.id
			WHERE firmware_make.name=%s AND firmware_model.name=%s
			''',
			(host_attrs[host][stack.firmware.MAKE_ATTR], host_attrs[host][stack.firmware.MODEL_ATTR])
		)
		# there's no firmware available
		if not rows:
			self.notify(
				f'Skipping {host} because no firmware exists for make'
				f' {host_attrs[host][stack.firmware.MAKE_ATTR]}'
				f' and model {host_attrs[host][stack.firmware.MODEL_ATTR]}.'
			)
		# there's more than one result, thus the desired version is ambiguous
		elif len(rows) > 1:
			self.notify(
				f'Skipping {host} because multiple firmware files exist'
				f' for make {host_attrs[host][stack.firmware.MAKE_ATTR]} and model'
				f' {host_attrs[host][stack.firmware.MODEL_ATTR]}. Please set'
				f' {stack.firmware.FIRMWARE_ATTR} to pin a desired firmware version.'
			)
		# else there's only one firmware for the make and model, so that is assumed to be the desired one
		else:
			# Ensure that if a version regex exists, that we check the version in the database matches.
			# Since they are optional, it could have been set after the fact and a bad version number was
			# snuck in.
			regex_obj = self.try_get_version_regex(
				make = host_attrs[host][stack.firmware.MAKE_ATTR],
				model = host_attrs[host][stack.firmware.MODEL_ATTR],
			)
			if regex_obj and not re.search(regex_obj.regex, rows[0][1], re.IGNORECASE):
				self.notify(
					f'Skipping {host} because the firmware version does not validate using the version_regex named {regex_obj.name}.'
					f" Check that your version_regex is correct using 'stack list firmware version_regex'."
				)
			# Skip if we're not being forced and the current firmware on the target matches the desired firmware.
			elif not force and rows[0][1] == host_current_firmwares[host]:
				self.notify(f"Skipping {host} because the current version {host_current_firmwares[host]} matches the desired version {rows[0][1]}")
			# else everything passes, set the return value with the metadata
			else:
				# Use resolve(strict = True) to force a exception if the file path doesn't exist.
				path = Path(rows[0][0]).resolve(strict = True)
				result = {
					'file': path,
					'version': rows[0][1],
					'make_imp': rows[0][2],
					'model_imp': rows[0][3],
					'attrs': host_attrs[host],
					'url': self.get_firmware_url(hostname = host, firmware_file = path),
					'force': force,
				}

		return result

	def get_host_specific_firmware(self, host, host_attrs, host_current_firmwares, force):
		result = None
		row = self.db.select(
			'''
			firmware.file, firmware.version, make_imp.name, model_imp.name
			FROM firmware
				INNER JOIN firmware_model
					ON firmware.model_id=firmware_model.id
				INNER JOIN firmware_make
					ON firmware_model.make_id=firmware_make.id
				LEFT JOIN firmware_imp as make_imp
					ON firmware_make.imp_id = make_imp.id
				LEFT JOIN firmware_imp as model_imp
					ON firmware_model.imp_id = model_imp.id
			WHERE firmware.version=%s AND firmware_make.name=%s AND firmware_model.name=%s
			''',
			(
				host_attrs[host][stack.firmware.FIRMWARE_ATTR],
				host_attrs[host][stack.firmware.MAKE_ATTR],
				host_attrs[host][stack.firmware.MODEL_ATTR],
			)
		)
		# if there were no results, there's no firmware file that exists for the pinned version number
		if not row:
			self.notify(
				f'Skipping {host} because pinned firmware version'
				f' {host_attrs[host][stack.firmware.FIRMWARE_ATTR]} for make'
				f' {host_attrs[host][stack.firmware.MAKE_ATTR]} and model'
				f' {host_attrs[host][stack.firmware.MODEL_ATTR]} does not exist.'
			)
		else:
			# Ensure that if a version regex exists, that we check the version in the database matches.
			# Since they are optional, it could have been set after the fact and a bad version number was
			# snuck in.
			regex_obj = self.try_get_version_regex(
				make = host_attrs[host][stack.firmware.MAKE_ATTR],
				model = host_attrs[host][stack.firmware.MODEL_ATTR],
			)
			if regex_obj and not re.search(regex_obj.regex, row[0][1], re.IGNORECASE):
				self.notify(
					f'Skipping {host} because the firmware version does not validate using the version_regex named {regex_obj.name}.'
					f" Check that your version_regex is correct using 'stack list firmware version_regex'."
				)
			# Skip if we're not being forced and the current firmware on the target matches the desired firmware.
			elif not force and row[0][1] == host_current_firmwares[host]:
				self.notify(f"Skipping {host} because the current version {host_current_firmwares[host]} matches the desired version {row[0][1]}")
			# else everything passes, set the return value with the metadata
			else:
				# Use resolve(strict = True) to force a exception if the file path doesn't exist.
				path = Path(row[0][0]).resolve(strict = True)
				result = {
					'file': path,
					'version': row[0][1],
					'make_imp': row[0][2],
					'model_imp': row[0][3],
					'attrs': host_attrs[host],
					'url': self.get_firmware_url(hostname = host, firmware_file = path),
					'force': force,
				}

		return result

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
		hosts_to_sync = {}
		host_attr_dict = self.getHostAttrDict(host = hosts)
		# grab all the current firmware versions
		current_firmware_versions = {
			result['host']: result['current firmware version']
			for result in self.call(command = 'list.host.firmware', args = hosts)
		}
		for host in hosts:
			# if make and model are not set, there's nothing to do for this host.
			if not host_attr_dict[host] or not all(
				key in host_attr_dict[host]
				for key in (stack.firmware.MAKE_ATTR, stack.firmware.MODEL_ATTR)
			):
				self.notify(
					f'Skipping {host} because {stack.firmware.MAKE_ATTR} and'
					f' {stack.firmware.MODEL_ATTR} attributes are not both set.'
				)
				continue

			# get the desired firmware version
			if stack.firmware.FIRMWARE_ATTR in host_attr_dict[host]:
				result = self.get_host_specific_firmware(
					host = host,
					host_attrs = host_attr_dict,
					host_current_firmwares = current_firmware_versions,
					force = force,
				)
				# If there was a result, add it to the hosts to sync
				if result is not None:
					hosts_to_sync[host] = result

			else:
				result = self.get_host_firmware(
					host = host,
					host_attrs = host_attr_dict,
					host_current_firmwares = current_firmware_versions,
					force = force,
				)
				# If there was a result, add it to the hosts to sync
				if result is not None:
					hosts_to_sync[host] = result

		# only run plugins if we have hosts to sync.
		if hosts_to_sync:
			self.runPlugins(args = hosts_to_sync)
