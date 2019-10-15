# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
from collections import OrderedDict
import json


class Command(stack.commands.dump.command):
	"""
	Dump the contents of the stacki database as json.

	This command dumps specifically the network data.
	For each network, output the name of the network, as
	well as its address, subnet mask, gateway, mtu, zone,
	and whether stacki is configured to serve DNS and
	DHCP/PXE for this network.

	<example cmd='dump network'>
	Dump json data for networks in the stacki database
	</example>

	<related>load</related>
	"""

	def run(self, params, args):

		dump = []
		for row in self.call('list.network'):
			dump.append(OrderedDict(
				name    = row['network'],
				address = row['address'],
				mask    = row['mask'],
				gateway = row['gateway'],
				mtu     = row['mtu'],
				zone    = row['zone'],
				dns     = self.str2bool(row['dns']),
				pxe     = self.str2bool(row['pxe'])))

		self.addText(json.dumps(OrderedDict(version = stack.version,
						    network = dump), indent=8))
