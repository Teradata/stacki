# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import OSArgProcessor
from stack.exception import ArgRequired, ArgUnique, ParamValue, CommandError


class command(OSArgProcessor, stack.commands.set.command):
	def getBootActionTypeOS(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'action')
		if len(args) != 1:
			raise ArgUnique(self, 'action')

		b_action = args[0]

		(b_type, b_os) = self.fillParams([
			('type', None, True),
			('os', '')
		])

		if b_type not in [ 'os', 'install' ]:
			raise ParamValue(self, 'type', '"os" or "install"')

		# If bootaction type is not os, then get the default
		# os so code doesn't break.
		if not b_os and b_type != 'os':
			b_os = self.os

		if b_os:
			b_os = self.getOSNames([b_os])[0]

		return (b_action, b_type, b_os)

	def actionExists(self, b_action, b_type, b_os=None):
		for row in self.call('list.bootaction', [
			b_action, f'type={b_type}', f'os={b_os}'
		]):
			if b_os == '':
				b_os = None

			if (
				b_action == row['bootaction'] and
				b_type == row['type'] and
				b_os == row['os']
			):
				return True

		return False

	def bootNameExists(self, b_action, b_type):
		return self.db.count(
			'(ID) from bootnames where name=%s and type=%s',
			(b_action, b_type)
		) > 0


class Command(command):
	"""
	Set a bootaction specification.

	<arg optional='0' type='string' name='action'>
	Label name for the bootaction. You can see the bootaction label names by
	executing: 'stack list bootaction [host(s)]'.
	</arg>

	<param type='string' name='os'>
	Operating System for the bootaction.
	</param>

	<param type='string' name='type'>
	Type of bootaction. Either 'os' or 'install'.
	</param>

	<param type='string' name='kernel'>
	The name of the kernel that is associated with this boot action.
	</param>

	<param type='string' name='ramdisk'>
	The name of the ramdisk that is associated with this boot action.
	</param>

	<param type='string' name='args'>
	The second line for a pxelinux definition (e.g., ks ramdisk_size=150000
	lang= devfs=nomount pxe kssendmac selinux=0)
	</param>

	<example cmd='set bootaction os type=os kernel="localboot 0"'>
	Set the 'os' bootaction.
	</example>

	<example cmd='set bootaction memtest type=os kernel="kernel memtest"'>
	Set the 'memtest' bootaction.
	</example>
	"""

	def run(self, params, args):
		(b_action, b_type, b_os) = self.getBootActionTypeOS(params, args)

		(b_kernel, b_ramdisk, b_args, force) = self.fillParams([
			('kernel',  '', True),
			('ramdisk', ''),
			('args',    ''),
			('force',   True)
		])

		force = self.str2bool(force)

		# If we don't force the update error out (AKA: the add command)
		existing = self.actionExists(b_action, b_type, b_os)
		if existing and not force:
			raise CommandError(self, 'action "%s" exists' % b_action)

		if not self.bootNameExists(b_action, b_type):
			self.db.execute(
				'insert into bootnames(name, type) values (%s, %s)',
				(b_action, b_type)
			)

		if not existing:
			if b_os:
				self.db.execute("""
					insert into bootactions(bootname, os) values (
						(select id from bootnames where name=%s and type=%s),
						(select id from oses where name=%s)
					)
				""", (b_action, b_type, b_os))
			else:
				self.db.execute("""
					insert into bootactions(bootname) values (
						(select id from bootnames where name=%s and type=%s)
					)
				""", (b_action, b_type))

		for flag, command in [
			(b_kernel, 'kernel'),
			(b_args, 'args'),
			(b_ramdisk, 'ramdisk')
		]:
			if flag:
				self.command(f'set.bootaction.{command}', [
					b_action,
					f'type={b_type}',
					f'os={b_os}',
					f'{command}={flag}'
				])
