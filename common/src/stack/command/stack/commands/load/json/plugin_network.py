# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
from stack.exception import CommandError

class Plugin(stack.commands.Plugin, stack.commands.Command):
	notifications = True

	def provides(self):
		return 'network'

	def requires(self):
		return [ 'software', 'environment', 'group' ]

	def run(self, args):

		# check if the user would like to import software data
		# if there are no args, assume the user would like to import everthing
		if args and 'network' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'network' in self.owner.data:
			import_data = self.owner.data['network']
		else:
			self.owner.log.info('no network data in the json document')
			return

		self.notify('\n\tLoading network\n')
		# TODO: sanitize validate
		for network in import_data:
			name = network['name'].strip()
			# the add network command requires at least name address and mask
			# if the network exists already we want to overwrite its information
			# so we first add the network then set everything else
			parameters = [
				name,
				f'address={network["address"]}',
				f'mask={network["netmask"]}',
			]
			self.owner.try_command('add.network', parameters, f'adding network {name}', 'exists')


			# now we set all of the attributes
			# if the field is empty in the json then remove the value
			if network['address']:
				self.owner.try_command('set.network.address', [ name, f'address={network["address"]}' ], f'adding {name} address', 'exists')
			else:
				self.owner.try_command('set.network.address', [ name, 'address=' ], f'adding {name} address', 'exists')

			if network['dns']:
				self.owner.try_command('set.network.dns', [ name, f'dns={network["dns"]}' ], f'adding {name} dns', 'exists')
			else:
				self.owner.try_command('set.network.dns', [ name, 'dns=' ], f'adding {name} dns', 'exists')

			if network['gateway']:
				self.owner.try_command('set.network.gateway', [ name, f'gateway={network["gateway"]}' ], f'adding {name} gateway', 'exists')
			else:
				self.owner.try_command('set.network.gateway', [ name, 'gateway=' ], f'adding {name} gateway', 'exists')

			if network['netmask']:
				self.owner.try_command('set.network.mask', [ name, f'mask={network["netmask"]}' ], f'adding {name} mask', 'exists')
			else:
				self.owner.try_command('set.network.mask', [ name, 'mask=' ], f'adding {name} mask', 'exists')

			if network['mtu']:
				self.owner.try_command('set.network.mtu', [ name, f'mtu={network["mtu"]}' ], f'adding {name} mtu', 'exists')
			else:
				self.owner.try_command('set.network.mtu', [ name, 'mtu=' ], f'adding {name} mtu', 'exists')

			if network['pxe']:
				self.owner.try_command('set.network.pxe', [ name, f'pxe={network["pxe"]}' ], f'adding {name} pxe', 'exists')
			else:
				self.owner.try_command('set.network.pxe', [ name, 'pxe=' ], f'adding {name} pxe', 'exists')

			if network['zone']:
				self.owner.try_command('set.network.zone', [ name, f'zone={network["zone"]}' ], f'adding {name} zone', 'exists')
			else:
				self.owner.try_command('set.network.zone', [ name, 'zone=' ], f'adding {name} zone', 'exists')
