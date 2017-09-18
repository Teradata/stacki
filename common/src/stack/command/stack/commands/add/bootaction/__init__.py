# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.add.command):
	"""
	Add a bootaction specification to the system.
	
	<param type='string' name='action'>
	Label name for the bootaction. You can see the bootaction label names by
	executing: 'stack list bootaction [host(s)]'.
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
	
	<example cmd='add bootaction action=os kernel="localboot 0"'>
	Add the 'os' bootaction.
	</example>
	
	<example cmd='add bootaction action=memtest command="memtest"'>
	Add the 'memtest' bootaction.
	</example>
	"""

	def run(self, params, args):

		self.command('set.bootaction', self._argv + [ 'force=no' ])
		return self.rc

		#	
		# regenerate all the pxe boot configuration files
		# including the default.
		#
#		self.command('set.host.boot', self.getHostnames())

