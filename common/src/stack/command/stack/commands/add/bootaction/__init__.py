# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.add.command):
	"""
	Add a bootaction specification to the system.

	<arg optional='0' type='string' name='action'>
	Label name for the bootaction. You can see the bootaction label names by
	executing: 'stack list bootaction [host(s)]'.
	</arg>
	
	<param type='string' name='os'>
	Operating System for the bootaction.
	The default os is Redhat.
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

	<example cmd='add bootaction os type=os kernel="localboot 0"'>
	Add the 'os' bootaction.
	</example>

	<example cmd='add bootaction memtest type=os kernel="kernel memtest"'>
	Add the 'memtest' bootaction.
	</example>
	"""

	def run(self, params, args):
		self.command('set.bootaction', self._argv + [ 'force=no' ])
		return self.rc
