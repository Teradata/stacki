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
		return 'appliance'

	def requires(self):
		return [ 'software', 'environment', 'group', 'network' ]

	def run(self, args):

		# check if the user would like to load appliance data
		if args and 'appliance' not in args:
			return

		# check if there is any appliance data to load
		if 'appliance' in self.owner.data:
			import_data = self.owner.data['appliance']
		else:
			self.owner.log.info('no appliance data in json file')
			return

		self.notify('\n\tLoading appliance\n')

		# add each appliance then set everything about it
		for appliance in import_data:
			appliance_name = appliance['name']
			self.owner.try_command('add.appliance', [ appliance_name ],f'adding appliance {appliance_name}', 'exists')

			# set all the atributes
			for attr in appliance['attrs']:
				parameters = [
				appliance_name,
					f'attr={attr["attr"]}',
					f'value={attr["value"]}'
				]
				if attr['type'] == 'shadow':
					parameters.append('shadow=True')

				self.owner.try_command('set.appliance.attr', parameters, f'setting appliance attr {attr["attr"]} for {appliance_name}', 'exists')

			# add all the routes
			for route in appliance['route']:
				parameters = [
					appliance_name,
					f'address={route["network"]}',
					f'gateway={route["gateway"]}',
					f'netmask={route["netmask"]}'
				]
				# if the add command returns false, run the remove command then re-run the add command
				if not self.owner.try_command('add.appliance.route', parameters, f'adding appliance route {route["network"]} to {appliance_name}', 'exists'):
					self.owner.try_command('remove.appliance.route', [ appliance_name, f'address={route["network"]}' ], f'removing appliance route {route["network"]} from {appliance_name}', 'exists')
					self.owner.try_command('add.appliance.route', parameters, f'adding appliance route {route["network"]} to {appliance_name}', 'exists')

			# add all of the rules, replacing them if they already exist
			for rule in appliance['firewall']:
				parameters = [
						appliance_name,
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
				# if the add command returns false, run the remove command then re-run the add command
				if not self.owner.try_command('add.appliance.firewall', parameters, f'adding appliance firewall rule {rule["action"]}', 'exists'):
					self.owner.try_command('remove.appliance.firewall', [ appliance_name, f'rulename={rule["name"]}' ], 'removing appliance firewall rule {rule["action"]}', 'exists')
					self.owner.try_command('add.appliance.firewall', parameters, f'adding appliance firewall rule {rule["action"]}', 'exists')

			# add all of the partition infromation
			# because add partition does not first check if it already exists, we remove all existing partitions then add the new ones
			device_list = []
			for partition in appliance['partition']:
				if partition['device'] not in device_list:
					device_list.append(partition['device'])
			for device in device_list:
				self.owner.try_command('remove.storage.partition', [ appliance_name, 'scope=appliance', f'device={device}' ], f'removing appliance partition {device} from {appliance_name}', 'exists')

			for partition in appliance['partition']:
				parameters = [
					appliance_name,
					f'device={partition["device"]}',
					f'partid={partition["partid"]}',
					f'size={partition["size"]}'
				]
				if partition['options']:
					parameters.append(f'options={partition["options"]}')
				if partition['mountpoint']:
					parameters.append(f'mountpoint={partition["mountpoint"]}')
				if partition ['fstype']:
					parameters.append(f'type={partition["fstype"]}')


				self.owner.try_command('add.storage.partition', parameters, f'adding appliance partition {device} to {appliance_name}', 'exists')

			# add all the controller information
			for controller in appliance['controller']:
				parameters = [
					appliance_name,
					f'arrayid={controller["arrayid"]}',
					f'raidlevel={controller["raidlevel"]}',
					f'slot={controller["slot"]}'
				]
				if controller['adapter']:
					parameters.append(f'adapter={controller["adapter"]}')
				if controller['enclosure']:
					parameters.append(f'enclosure={controller["enclosure"]}')
				if controller['options']:
					parameters.append(f'options={controller["options"]}')
				self.owner.try_command('add.storage.controller', parameters, f'adding appliance controller to {appliance_name}', 'exists')
