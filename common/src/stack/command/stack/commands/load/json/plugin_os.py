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
		return 'os'

	def requires(self):
		return [ 'software', 'environment', 'group', 'network', 'appliance' ]

	def run(self, args):

		# check if the user would like to import os data
		# if there are no args, assume the user would like to import everthing
		if args and 'os' not in args:
			return
		# self.owner.data contains the data from the json file defined in init
		# check if there is any os data in the import file
		if 'os' in self.owner.data:
			import_data = self.owner.data['os']
		else:
			self.owner.log.info('no os data in json file')
			return

		self.notify('\n\tLoading os\n')
		for os in import_data:
			os_name= os['name']

			# set os attrs
			for attr in os['attrs']:
				# determine if this is a shadow attr by looking at the type
				if attr['type'] == 'shadow':
					attr_shadow = True
				else:
					attr_shadow = False
				parameters = [
					os_name,
					f'attr={attr["attr"]}',
					f'value={attr["value"]}',
					f'shadow={attr_shadow}',
				]
				self.owner.try_command('set.os.attr', parameters, f'setting os attr {attr}', 'exists')

			# set os routes
			for route in os['route']:
				parameters = [
					os_name,
					f'address={route["network"]}',
					f'gateway={route["gateway"]}',
					f'netmask={route["netmask"]}',
				]
				self.owner.try_command('add.os.route', parameters, f'adding os route {route}', 'exists')

			# add os firewall rules. If the rule exists, remove it and replace it with the one in the json
			for rule in os['firewall']:
				parameters = [
					os_name,
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
				if not self.owner.try_command('add.os.firewall', parameters, f' adding os firewall rule {rule}', 'exists'):
					self.owner.try_command('remove.os.firewall', [ os_name, f'rulename={rule["name"]}' ], 'removing os firewall rule {rule["action"]}', 'exists')
					self.owner.try_command('add.os.firewall', parameters, f' adding os firewall rule {rule}', 'exists')

			# add os partitions
			for partition in os['partition']:
				parameters = [
					os_name,
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

				self.owner.try_command('add.storage.partition', parameters, f'adding os partition {partition}', 'exists')

			# add os controllers
			for controller in os['controller']:
				parameters = [
					os_name,
					f'arrayid={controller["arrayid"]}',
				]
				if controller['adapter']:
					parameters.append(f'adapter={controller["adapter"]}')
				if controller['enclosure']:
					parameters.append(f'enclosure={controller["enclosure"]}')
				if controller['raidlevel']:
					parameters.append(f'raidlevel={controller["raidlevel"]}')
				if controller['slot']:
					parameters.append(f'slot={controller["slot"]}')
				self.owner.try_command('add.storage.controller', parameters, f'adding os controller {controller}', 'exists')
