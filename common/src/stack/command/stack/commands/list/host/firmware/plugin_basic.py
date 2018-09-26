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
		hosts, expanded, hashit = args

		keys = []
		host_info = {host: [] for host in hosts}

		if expanded:
			# This is used by the MessageQ as a permanent handle on
			# Redis keys. This allows both the networking and names
			# of hosts to change and keeps the mq happy -- doesn't
			# break the status in 'list host'.
			keys.append('id')
			for name, node_id in self.db.select('name, id FROM nodes WHERE name in %s', (hosts, )):
				host_info[name].append(node_id)

		for row in self.db.select(
			"""
			nodes.name, appliances.name, oses.name, boxes.name
			FROM nodes
				LEFT JOIN appliances ON nodes.appliance=appliances.id
				LEFT JOIN boxes ON nodes.box=boxes.id
				LEFT JOIN environments on nodes.environment=environments.id
				LEFT JOIN oses ON boxes.os=oses.id
			WHERE nodes.name IN %s
			""",
			(hosts, )
		):
			host_info[row[0]].extend(row[1:])

		keys.extend(['appliance', 'os', 'box'])

		for host in hosts:
			host_firmware_attrs = {
				key: value
				for (key, value) in self.owner.getHostAttrDict(host = host)[host].items()
				if key in (stack.firmware.MAKE_ATTR, stack.firmware.MODEL_ATTR, stack.firmware.FIRMWARE_ATTR)
			}
			# if make and model are not set, there's nothing to look up.
			if not host_firmware_attrs or not all(
				key in host_firmware_attrs
				for key in (stack.firmware.MAKE_ATTR, stack.firmware.MODEL_ATTR)
			):
				host_info[host].append(None)
				continue

			# get the desired firmware version
			if stack.firmware.FIRMWARE_ATTR in host_firmware_attrs:
				row = self.owner.db.select(
					'''
					firmware.version
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
					host_info[host].append(
						f"{host_firmware_attrs[stack.firmware.FIRMWARE_ATTR]} (doesn't exist, did you forget to add it?)"
					)
				else:
					# Ensure that if a version regex exists, that we check the version in the database matches.
					# Since they are optional, it could have been set after the fact and a bad version number was
					# snuck in.
					regex_obj = self.owner.try_get_version_regex(
						make = host_firmware_attrs[stack.firmware.MAKE_ATTR],
						model = host_firmware_attrs[stack.firmware.MODEL_ATTR],
					)
					if regex_obj and not re.search(regex_obj.regex, row[0][0], re.IGNORECASE):
						host_info[host].append(
							f"{row[0][0]} (Doesn't validate using the version_regex named {regex_obj.name} and will be ignored by sync)"
						)
					else:
						host_info[host].append(row[0][0])

			else:
				rows = self.owner.db.select(
					'''
					firmware.version
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
					host_info[host].append(None)
				# there's more than one result, thus the desired version is ambiguous
				elif len(rows) > 1:
					host_info[host].append(f'ambiguous, set {stack.firmware.FIRMWARE_ATTR} to pin a version')
				# else there's only one firmware for the make and model, so that is assumed to be the desired one
				else:
					# Ensure that if a version regex exists, that we check the version in the database matches.
					# Since they are optional, it could have been set after the fact and a bad version number was
					# snuck in.
					regex_obj = self.owner.try_get_version_regex(
						make = host_firmware_attrs[stack.firmware.MAKE_ATTR],
						model = host_firmware_attrs[stack.firmware.MODEL_ATTR],
					)
					if regex_obj and not re.search(regex_obj.regex, rows[0][0], re.IGNORECASE):
						host_info[host].append(
							f"{rows[0][0]} (Doesn't validate using the version_regex named {regex_obj.name} and will be ignored by sync)"
						)
					else:
						host_info[host].append(rows[0][0])

		keys.append('desired firmware version')

		return { 'keys' : keys, 'values': host_info }
