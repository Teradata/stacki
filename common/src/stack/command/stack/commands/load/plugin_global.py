# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
from stack.exception import CommandError

class __Plugin(stack.commands.Plugin, stack.commands.Command):
	def provides(self):
		return 'global'
	def requires(self):
		return [ 'software', 'environment', 'group', 'network', 'appliance', 'os' ]

	def run(self, args):

		# check if the user would like to import global data
		if args and 'global' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'global' in self.owner.data:
			import_data = self.owner.data['global']
		else:
			self.owner.log.info('no global data in json file')
			return

		self.notify('\n\tLoading global')
		for scope in import_data:
			# check to make sure the scope is valid
			if scope == 'attrs':
				for attr in import_data[scope]:
					attr_type = attr['type']

					if attr_type == 'shadow':
						attr_shadow = True
					else:
						attr_shadow = False
					parameters = [
						f'attr={attr["attr"]}',
						f'value={attr["value"]}',
						f'shadow={attr_shadow}',
						]
					self.owner.try_command('set.attr', parameters, f'setting global attr {attr["attr"]}', 'exists')


			elif scope == 'route':
				for route in import_data[scope]:
					parameters = [
						f'address={route["network"]}',
						f'gateway={route["gateway"]}',
						f'netmask={route["netmask"]}',
						]
					self.owner.try_command('add.route', parameters, f'adding global route {route["network"]}', 'exists')


			elif scope == 'firewall':
				for rule in import_data[scope]:
					parameters = [
					f'action={rule["action"]}',
					f'chain={rule["chain"]}',
					f'protocol={rule["protocol"]}',
					f'service={rule["service"]}',
					f'network={rule["network"]}',
					f'output-network={rule["output-network"]}',
					f'rulename={rule["name"]}',
					f'table={rule["table"]}'
					]
					if rule['flags']:
						parameters.append(f'flags={rule["flags"]}')
					if rule['comment']:
						parameters.append(f'comment={rule["comment"]}')
					# if the firewall rule already exists, we want to remove it and add the one in the json
					# currently firewall has no set commands
					if not self.owner.try_command('add.firewall', parameters, f'adding global firewall fule {rule["name"]}', 'exists'):
						self.owner.try_command('remove.firewall', [ f'rulename={rule["name"]}' ], f'removing pre-existing global firewall fule {rule["name"]}', 'exists')
						self.owner.try_command('add.firewall', parameters, f'adding global firewall fule {rule["name"]}', 'exists')


			elif scope == 'partition':
				for partition in import_data[scope]:
					parameters = [
						f'device={partition["device"]}',
						f'partid={partition["partid"]}',
						f'size={partition["size"]}',
					]
					if partition['options']:
						parameters.append(f'options={partition["options"]}')
					if partition['mountpoint']:
						parameters.append(f'mountpoint={partition["mountpoint"]}')
					if partition ['fstype']:
						parameters.append(f'type={partition["fstype"]}')
					self.owner.try_command('add.storage.partition', parameters, f'adding global partition {partition}', 'exists')


			elif scope == 'controller':
				for controller in import_data[scope]:
					parameters = [f'arrayid={controller["arrayid"]}',
						f'raidlevel={controller["raidlevel"]}',
						f'slot={controller["slot"]}',
					]
					if controller['adapter']:
						parameters.append(controller['adapter'])
					if controller['enclosure']:
						parameters.append(controller['enclosure'])
					if controller['options']:
						parameters.append(controller['options'])

					self.owner.try_command('add.storage.controller', parameters, f'adding global controller {controller["arrayid"]}', 'exists')

			else:
				self.owner.log.info(f'error potentially invalid entry in json. {scope} is not a valid global scope')

