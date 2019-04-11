# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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

class Command(stack.commands.remove.host.firmware.command):
	"""
	Removes firmware mappings.

	<arg type='string' name='host' repeat='1'>
	Zero or more hosts to have their mapped firmware versions removed.
	If no hosts are specified, all mappings for all hosts are removed.
	</arg>

	<param type='string' name='versions'>
	Zero or more firmware versions to be unmapped. Multiple versions should be specified as a comma separated list.
	If no versions are specified, all will be removed.
	If one or more versions are specified, the make and model parameters are required.
	</param>

	<param type='string' name='make'>
	The optional make of the firmware to unmap.
	If this is specified but no versions or model are specified, this will remove all firmware mappings that match the make.
	</param>

	<param type='string' name='model'>
	The optional model of the firmware to unmap.
	If this is specified, make is required.
	If no versions are specified but make and model are specified, all firmwares for that make and model will be removed.
	</param>

	<example cmd="remove host firmware mapping">
	Removes all firmware mappings for all hosts.
	</example>

	<example cmd="remove host firmware mapping switch-13-11 switch-13-12 versions=3.6.5002,3.6.8010 make=mellanox model=m7800">
	Unmaps the firmware versions 3.6.5002 and 3.6.8010 for the mellanox m7800 make and model from the hosts named switch-13-11 and switch-13-12.
	</example>

	<example cmd="remove host firmware mapping make=mellanox model=m7800">
	Unmaps all firmware for the mellanox make and m7800 model from all hosts.
	</example>

	<example cmd="remove host firmware mapping switch-13-11 make=mellanox">
	Unmaps all of the firmware for the mellanox make from the host named switch-13-11.
	</example>

	<example cmd="remove host firmware mapping make=mellanox">
	Unmaps all of the firmware for the mellanox make from all hosts.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
