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

		#check if the user would like to import software data
		#if there are no args, assume the user would like to import everthing
		if args and 'network' not in args:
			return

		#self.owner.data contains the data from the json file defined in init
		#check if there is any software data before we go getting all kinds of key errors
		if 'network' in self.owner.data:
			import_data = self.owner.data['network']
		else:
			print('no network data in the json document')
			return

		#TODO: sanitize validate
		for network in import_data:
			name = network['name'].strip()
			try:
				self.owner.command('add.network', [ name, 
							f'address={network["address"]}', 
							f'mask={network["netmask"]}', 
							f'dns={network["dns"]}', 
							f'gateway={network["gateway"]}', 
							f'mtu={network["mtu"]}', 
							f'pxe={network["pxe"]}', 
							f'zone={network["zone"]}' ])
				print(f'success adding network {network}')
				self.owner.successes += 1

			except Exception as e:
				if 'exists' in str(e):
					print(f'warning adding network {network}: {e}')
					self.owner.warnings += 1
				else:
					print(f'error adding network {network}: {e}')
					self.owner.errors += 1

