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
import json

class Command(stack.commands.Command):
	"""
	Export data into a single json document. If no arguments are given
	then all scopes will be exported.

	<arg optional='0' type='string' name='software'>
	Export pallet, cart, and box data
	</arg>

	<arg optional='0' type='string' name='host'>
	Export name, rack, rank, interface, attr, firewall, box, appliance,
	comment, metadata, environment, osaction, route, group, partition,
	and controller data for each host.
	</arg>

	<arg optional='0' type='string' name='network'>
	Export name, address, gateway, netmask, dsn, pxe, mtu, and zone
	data for each network.
	</arg>

	<arg optional='0' type='string' name='global'>
	Export attr, route, firewall, partition, and controller data for
	the global scope.
	</arg>

	<arg optional='0' type='string' name='os'>
	Export name, attr, route, firewall, partition, and controller
	data for each os.
	</arg>

	<arg optional='0' type='string' name='appliance'>
	Export name, attr, route, firewall, partition, and controller
	data for each appliance.
	</arg>

	<arg optional='0' type='string' name='group'>
	Export name data for each group.
	</arg>

	<arg optional='0' type='string' name='bootaction'>
	Export name, kernel, ramdisk, type, arg, and os data for each
	bootaction.
	</arg>
	"""
	def run(self,params, args):
		#runPlugins() returns a list of tuples where tuple[0] is the plugin name and
		#tuple[1] is the return value
		#each plugin examins 'args' to determine if it runs or not
		data = self.runPlugins(args)
		document_prep = {}
		for plugin in data:
			document_prep.update(plugin[1])

		self.beginOutput()
		self.addOutput(None,json.dumps(document_prep))
		self.endOutput(trimOwner=True)


