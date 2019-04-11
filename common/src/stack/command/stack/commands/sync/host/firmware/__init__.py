# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
from pathlib import Path
from collections import namedtuple
import stack.commands
import stack.firmware
from stack.argument_processors.firmware import FirmwareArgumentProcessor

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

	def get_host_firmwares(self, common_key, hosts, host_attrs, host_current_firmwares, force):
		results = {}
		# The firmware information for a given host + make + model combination.
		FirmwareInfo = namedtuple(
			"FirmwareInfo", (
				# Can potentially support multiple firmware files
				"firmware_files",
				"current_version",
				"imp",
				"host_attrs",
				"force",
				"frontend_ip",
			)
		)
		# The information for the firmware file to be applied.
		FirmwareFile = namedtuple(
			"FirmwareFile", (
				"file",
				"version",
				"url",
			)
		)
		for row in self.db.select(
				"""
				nodes.Name, firmware_make.name, firmware_model.name, firmware.version, firmware.file, firmware_imp.name
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
			host_make_model = common_key(*row[:3])
			version, firmware_file, imp = row[3:]
			# Use resolve(strict = True) to force a exception if the file path doesn't exist.
			path = Path(firmware_file).resolve(strict = True)
			# If the key does not already exist in the map, add it. Otherwise, update the existing information.
			if host_make_model in results:
				results[host_make_model].firmware_files.add(
					FirmwareFile(
						file = path,
						version = version,
						url = self.get_firmware_url(hostname = host_make_model.host, firmware_file = path),
					)
				)
			else:
				results[host_make_model] = FirmwareInfo(
					current_version = host_current_firmwares[host_make_model],
					imp = imp,
					host_attrs = host_attrs[host_make_model.host],
					force = force,
					frontend_ip = self.get_common_frontend_ip(hostname = host_make_model.host),
					firmware_files = {
						FirmwareFile(
							file = path,
							version = version,
							url = self.get_firmware_url(hostname = host_make_model.host, firmware_file = path),
						)
					}
				)

		# Perform post processing and validation now that we have all the info from the DB
		invalid_mappings = set()
		for host_make_model, firmware_info in results.items():
			# don't allow multiple firmware versions for a host + make + model combo unless force is specified.
			if not force and len(firmware_info.firmware_files) > 1:
				invalid_mappings.add(host_make_model)
				self.notify(
					f"The host + make + model combination of {host_make_model.host} {host_make_model.make} {host_make_model.model}"
					f" has multiple firmware versions mapped to it and is being skipped. Check your configuration or use force=true to override."
				)
				continue

			# Ensure that if a version regex exists, that we check the version in the database matches.
			# Since they are optional, it could have been set after the fact and a bad version number was
			# snuck in.
			regex_obj = self.try_get_version_regex(
				make = host_make_model.make,
				model = host_make_model.model,
			)
			for firmware_file in firmware_info.firmware_files:
				# force does not override the regex check because version_regexes are optional.
				if regex_obj and not re.search(regex_obj.regex, firmware_file.version, re.IGNORECASE):
					invalid_mappings.add(host_make_model)
					self.notify(
						f"Skipping The host + make + model combination of {host_make_model.host} {host_make_model.make} {host_make_model.model}"
						f" because the firmware version {firmware_file.version} does not validate using the version_regex named {regex_obj.name}."
						f" Check that your version_regex is correct using 'stack list firmware version_regex'."
					)
					break
				# don't upgrade to the same version for a host + make + model combo unless force is specified.
				if not force and firmware_file.version == host_current_firmwares[host_make_model]:
					invalid_mappings.add(host_make_model)
					self.notify(
						f"Skipping The host + make + model combination of {host_make_model.host} {host_make_model.make} {host_make_model.model}"
						f" because the current version {host_current_firmwares[host_make_model]} matches the desired version {firmware_file.version}"
						f" Use force=true to override."
					)
					break

		# Notify about the hosts being skipped because of no mapped firmware.
		hosts_with_mapped_firmware = [host_make_model.host for host_make_model in results]
		for host in hosts:
			if host not in hosts_with_mapped_firmware:
				self.notify(
					f"Skipping {host} because no firmware is mapped to it."
				)

		# Drop the invalid mappings before returning the results.
		for host_make_model in invalid_mappings:
			results.pop(host_make_model)

		return results

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
		host_attrs = self.getHostAttrDict(host = hosts)
		# grab all the current firmware versions
		CommonKey = namedtuple("CommonKey", ("host", "make", "model"))
		current_firmware_versions = {
			CommonKey(result["host"], result["make"], result["model"]): result["current_firmware_version"]
			for result in self.call(command = 'list.host.firmware', args = hosts)
		}

		# get the firmware info for all hosts
		results = self.get_host_firmwares(
			common_key = CommonKey,
			hosts = hosts,
			host_attrs = host_attrs,
			host_current_firmwares = current_firmware_versions,
			force = force,
		)

		# only run plugins if we have hosts to sync.
		if results:
			self.runPlugins(args = results)
