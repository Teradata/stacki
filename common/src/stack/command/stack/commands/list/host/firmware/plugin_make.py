# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):
	"""Runs the make implementation based on the make attribute for the host and returns the output."""

	def provides(self):
		return 'version'

	def requires(self):
		return ['basic']

	def run(self, args):
		pass
		# firmware_attrs = ['component.make', 'component.model', 'component.firmware_version']
		# hosts, expanded, hashit = args

		# host_info = dict.fromkeys(hosts)

		# for host in hosts:
		# 	host_firmware_attrs = {
		# 		key: value
		# 		for key, value in self.owner.getHostAttrDict(host = host).items()
		# 		if key in firmware_attrs
		# 	}
		# 	# if make and model are not set, there's nothing to look up.
		# 	if not host_firmware_attrs or not all(key in host_firmware_attrs for key in firmware_attrs[0:2]):
		# 		host_info[host] = [None, None]
		# 		continue

		# 	# store the current version information
		# 	host_info[host] = [self.owner.runImplementation(name = host_firmware_attrs[host]['component.make'], args = host)]
		# 	# get the available version information
		# 	if
		# 	host_info[host].append(
		# 		self.owner.db.select(
		# 			'''
		# 			firmware.version
		# 			FROM firmware
		# 				INNER JOIN firmware_model
		# 					ON firmware.model_id=firmware_model.id
		# 				INNER JOIN firmware_make
		# 					ON firmware_model.make_id=firmware_make.id
		# 			WHERE firmware.version=%s AND firmware_make.name=%s AND firmware_model.name=%s
		# 			''',

		# 		)
		# 	)

		# return {'keys'  : ['Current Version','Available Version'],
		# 	'values': host_info }


RollName = "stacki"
