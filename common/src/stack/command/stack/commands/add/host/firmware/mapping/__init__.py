# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands

class Command(stack.commands.add.host.firmware.command):
	"""
	Maps firmware files to hosts so 'stack sync host firmware' can find them.

	<arg type='string' name='host' repeat='1'>
	One or more hostnames to associate with a firmware version.
	</arg>

	<param type='string' name='version'>
	The firmware version to map to the provided hosts.
	</param>

	<param type='string' name='make'>
	The make of the firmware version.
	</param>

	<param type='string' name='model'>
	The model for the given make of the firmware version.
	</param>

	<example cmd="add host firmware mapping switch-11-13 version=3.6.2010 make=mellanox model=m7800">
	Maps firmware version 3.6.2010 for make mellanox and model m7800 to the host with the name switch-11-3.
	</example>

	<example cmd="add host firmware mapping switch-11-13 switch-10-15 version=3.6.2010 make=mellanox model=m7800">
	This is the same as the previous example except the firmware will be mapped to both switch-11-3 and switch-10-15.
	</example>

	<example cmd="add host firmware mapping a:switch version=3.6.2010 make=mellanox model=m7800">
	This is the same as the previous example except the firmware will be mapped to all hosts that are switch appliances.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
