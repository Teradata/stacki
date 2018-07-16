# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
from stack.exception import CommandError

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'network'

	def requires(self):
		return [ 'software', 'environment', 'group' ]

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
				#the add network command requires at least name address and mask
				#if the network exists already we want to overwrite its information
				#so we first add the network then set everything
				self.owner.command('add.network', [
								name,
								f'address={network["address"]}',
								f'mask={network["netmask"]}'
				])
				print(f'success adding network {name}')
				self.owner.successes += 1
			except CommandError as e:
				if 'exists' in str(e):
					print(f'warning adding network {name}: {e}')
					self.owner.warnings += 1
				else:
					print(f'error adding network {name}: {e}')
					self.owner.errors += 1

			try:
				#now we set all of the attributes
				#if the network existed already in the database we will overwrite everything about it
				if network['address']:
					self.owner.command('set.network.address', [ name, f'address={network["address"]}' ])
					print(f'success adding {name} address')
					self.owner.successes += 1
				if network['dns']:
					self.owner.command('set.network.dns', [ name, f'dns={network["dns"]}' ])
					print(f'success adding {name} dns')
					self.owner.successes += 1
				if network['gateway']:
					self.owner.command('set.network.gateway', [ name, f'gateway={network["gateway"]}' ])
					print(f'success adding {name} gateway')
					self.owner.successes += 1
				if network['netmask']:
					self.owner.command('set.network.mask', [ name, f'mask={network["netmask"]}' ])
					print(f'success adding {name} mask')
					self.owner.successes += 1
				if network['mtu']:
					self.owner.command('set.network.mtu', [ name, f'mtu={network["mtu"]}' ])
					print(f'success adding {name} mtu')
					self.owner.successes += 1
				if network['pxe']:
					self.owner.command('set.network.pxe', [ name, f'pxe={network["pxe"]}' ])
					print(f'success adding {name} pxe')
					self.owner.successes += 1
				if network['zone']:
					self.owner.command('set.network.zone', [ name, f'zone={network["zone"]}' ])
					print(f'success adding {name} zone')
					self.owner.successes += 1

			except CommandError as e:
				if 'exists' in str(e):
					print(f'warning setting network {name}: {e}')
					self.owner.warnings += 1
				else:
					print(f'error setting network {name}: {e}')
					self.owner.errors += 1

