# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.argument_processors.firmware import FirmwareArgumentProcessor

class command(stack.commands.sync.command, FirmwareArgumentProcessor):
	pass


class Command(command):
	"""
	Syncs the firmware files on the frontend with what the expected firmware is in the stacki database

	<arg optional='1' type='string' name='version' repeat='1'>
	Zero or more firmware versions to sync. If none are specified, all firmware files tracked by stacki will be synced.
	</arg>

	<param type='string' name='make'>
	The make of the firmware versions to be synced. This is required if version arguments are specified.
	</param>

	<param type='string' name='model'>
	The model of the firmware versions to be synced. This is required if version arguments are specified.
	</param>

	<example cmd='sync firmware 3.6.8010 make=Mellanox model=m7800'>
	Makes sure the firmware file with version 3.6.8010 for Mellanox m7800 devices exists on the filesystem
	and has the correct hash. It will be re-fetched from the source if necessary.
	</example>

	<example cmd='sync firmware'>
	Syncs all known firmware files, checking that they exist on the filesystem and have the correct hash.
	They will be re-fetched from the source if necessary.
	</example>
	"""

	def run(self, params, args):
		self.notify('Sync Firmware')
		self.runPlugins(args = (params, args))
