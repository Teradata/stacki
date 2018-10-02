# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError


class Command(stack.commands.set.bootaction.command):
	"""
	Updates the ramdisk for a bootaction.

	<arg type='string' name='action' repeat='0' optional='0'>
	Name of the bootaction that needs to be updated.
	</arg>

	<param type='string' name='os'>
	os type of the bootaction.
	</param>

	<param type='string' name='type'>
	type of the bootaction. Can be install or os.
	</param>

	<param type='string' name='ramdisk' optional='0'>
	Updated ramdisk value.
	</param>

	<example cmd='set bootaction ramdisk memtest ramdisk="initrd.img-5.0-7.x-x86_64" type="os" os="redhat"'>
	Sets the ramdisk for bootaction named memtest with type="os" and os="redhat"
	to be "initrd.img-5.0-7.x-x86_64".
	</example>
	"""

	def run(self, params, args):
		(b_action, b_type, b_os) = self.getBootActionTypeOS(params, args)

		(b_ramdisk, ) = self.fillParams([ ('ramdisk', '', True) ])

		if not self.actionExists(b_action, b_type, b_os):
			raise CommandError(self, 'action "%s" does not exist' % b_action)

		if b_os:
			self.db.execute("""
				update bootactions set ramdisk=%s
				where os=(
					select id from oses where name=%s
				)
				and bootname=(
					select id from bootnames where name=%s and type=%s
				)
			""", (b_ramdisk, b_os, b_action, b_type))
		else:
			self.db.execute("""
				update bootactions set ramdisk=%s
				where os is NULL and bootname=(
					select id from bootnames where name=%s and type=%s
				)
			""", (b_ramdisk, b_action, b_type))
