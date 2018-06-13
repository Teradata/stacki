# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):
	
	def provides(self):
		return 'network'

	
	def run(self, args):

		if args and 'network' not in args:
			return

		
		if 'network' in self.owner.data:
			import_data = self.owner.data['network']
		else:
			print('no network data in the json document')
			return

		#sanitize validate
		for network in import_data:
			name = network['name'].strip()
			address = network['address']
			mask = network['netmask']
			dns = network['dns']
			gateway = network['gateway']
			mtu = network['mtu']
			pxe = network['pxe']
			zone = network['zone']

			self.owner.command('add.network', [ name, f'address={address}', f'mask={mask}', 
								f'dns={dns}', f'gateway={gateway}', f'mtu={mtu}', 
								f'pxe={pxe}', f'zone={zone}' ])


RollName = "stacki"
