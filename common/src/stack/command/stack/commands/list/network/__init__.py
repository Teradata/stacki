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
from stack.commands import NetworkArgProcessor


class Command(NetworkArgProcessor, stack.commands.list.command):
	"""
	List the defined networks for this system.

	<arg optional='1' type='string' name='network' repeat='1'>
	Zero, one or more network names. If no network names are supplied,
	info about all the known networks is listed.
	</arg>
	
	<example cmd='list network private'>
	List network info for the network named 'private'.
	</example>

	<example cmd='list network'>
	List info for all defined networks.
	</example>
	"""

	def run(self, params, args):

		(dns, pxe) = self.fillParams([('dns', None),
					      ('pxe', None)])

		if dns:
			dns = self.str2bool(dns)
		if pxe:
			pxe = self.str2bool(pxe)
			
		self.beginOutput()

		networks = {}
		for row in self.db.select("""
			name, address, mask, gateway, mtu, zone,
			if(dns, 'True', 'False'),
			if(pxe, 'True', 'False')
			from subnets
			"""):
			network = {}
			network['name']    = row[0]
			network['address'] = row[1]
			network['mask']    = row[2]
			network['gateway'] = row[3]
			network['mtu']     = row[4]
			network['zone']    = row[5]
			network['dns']     = self.str2bool(row[6])
			network['pxe']     = self.str2bool(row[7])
			if row[0]:
				networks[row[0]] = network

		for net in self.getNetworkNames(args):
			network = networks[net]

			if not (dns is None or network['dns'] == dns):
				continue
			if not (pxe is None or network['pxe'] == pxe):
				continue
			
			self.addOutput(network['name'], [ network['address'],
							network['mask'],
							network['gateway'],
							network['mtu'],
							network['zone'],
							network['dns'],
							network['pxe'] ])     
			
		self.endOutput(trimOwner=False, header=['network', 'address', 'mask', 'gateway',
					       'mtu', 'zone', 'dns', 'pxe'])
