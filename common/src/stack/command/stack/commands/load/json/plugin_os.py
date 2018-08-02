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
			for attr in os['attrs']:
				# determine if this is a shadow attr by looking at the type
				if attr['type'] == 'shadow':
					attr_shadow = True
				else:
					attr_shadow = False
				try:
					self.owner.command('set.os.attr', [
									os_name,
									f'attr={attr["attr"]}',
									f'value={attr["value"]}',
									f'shadow={attr_shadow}'
					])
					self.owner.log.info(f'success setting os attr {attr}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning setting os attr {attr}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error setting os attr {attr}: {e}')
						self.owner.errors += 1

			for route in os['route']:
				try:
					self.owner.command('add.os.route', [
									os_name,
									f'address={route["network"]}',
									f'gateway={route["gateway"]}',
									f'netmask={route["netmask"]}'
					])
					self.owner.log.info(f'success adding os route {route}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding os route {route}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding os route {route}: {e}')
						self.owner.errors += 1


			for rule in os['firewall']:
				try:
					self.owner.command('add.os.firewall', [
									os_name,
									f'action={rule["action"]}',
									f'chain={rule["chain"]}',
									f'protocol={rule["protocol"]}',
									f'service={rule["service"]}',
									f'network={rule["network"]}',
									f'output-network={rule["output-network"]}',
									f'rulename={rule["name"]}',
									f'table={rule["table"]}'
					])
					self.owner.log.info(f'success adding os firewall rule {rule}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding os firewall rule {rule}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding os firewall rule {rule}: {e}')
						self.owner.errors += 1

			for partition in os['partition']:
				try:
					self.owner.log.info('adding os partition...')
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

					self.owner.command('add.storage.partition', parameters)
					self.owner.log.info(f'success adding os partition {partition}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding os partition: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding os partition: {e}')
						self.owner.errors += 1


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


				try:
					self.owner.log.info('adding os controller...')
					self.owner.command('add.storage.controller', parameters)
					self.owner.log.info(f'success adding os controller {controller}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding os ontroller: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding os controller: {e}')
						self.owner.errors += 1
