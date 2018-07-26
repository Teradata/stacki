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
			try:
				self.owner.command('add.appliance', [ appliance_name ])
				self.owner.log.info(f'success adding appliance {appliance_name}')
				self.owner.successes += 1

			except CommandError as e:
				if 'exists' in str(e):
					self.owner.log.info(f'warning adding appliance {appliance_name}: {e}')
					self.owner.warnings += 1
				else:
					self.owner.log.info(f'error adding appliance {appliance_name}: {e}')
					self.owner.errors += 1


			for attr in appliance['attrs']:
				try:
					parameters = [
						appliance_name,
						f'attr={attr["attr"]}',
						f'value={attr["value"]}'
					]
					if attr['type'] == 'shadow':
						parameters.append('shadow=True')

					self.owner.command('set.appliance.attr', parameters)
					self.owner.log.info(f'success setting {appliance_name} attr {attr["attr"]}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning setting {appliance_name} attr {attr["attr"]}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error setting {appliance_name} attr {attr["attr"]}: {e}')
						self.owner.errors += 1


			for route in appliance['route']:
				try:
					parameters = [
						appliance_name,
						f'address={route["network"]}',
						f'gateway={route["gateway"]}',
						f'netmask={route["netmask"]}'
					]

					self.owner.command('add.appliance.route', parameters)
					self.owner.log.info(f'success adding appliance route {route}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						# the route exists so we want to remove it and add our own
						try:
							self.owner.command('remove.appliance.route', [ appliance_name, f'address={route["network"]}' ])
							self.owner.command('add.appliance.route', parameters)
							self.owner.log.info(f'success replacing appliance route {route}')
						except:
							self.owner.log.info(f'error adding appliance route: {e}')
							self.owner.errors += 1
					else:
						self.owner.log.info(f'error adding appliance route: {e}')
						self.owner.errors += 1


			for rule in appliance['firewall']:
				try:
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

					self.owner.command('add.appliance.firewall', parameters)
					self.owner.log.info(f'success adding appliance firewall rule {rule["name"]}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						# the firewall rule already exists so we want to remove it and add the new one
						try:

							self.owner.command('remove.appliance.firewall', [ appliance_name, f'rulename={rule["name"]}' ])

							self.owner.command('add.appliance.firewall', parameters)
							self.owner.log.info(f'success replacing appliance firewall rule {rule["name"]}')
							self.owner.successes += 1
						except CommandError as e:
							self.owner.log.info(f'error adding appliance firewall rule {rule["name"]}: {e}')
							self.owner.errors += 1
					else:
						self.owner.log.info(f'error adding appliance firewall rule {rule["name"]}: {e}')
						self.owner.errors += 1

			# the add partition commmand does not check to see if the value is already in the database
			# to remedy this we will blow away all the existing partition info and replace it with ours
			device_list = []
			for partition in appliance['partition']:
				if partition['device'] not in device_list:
					device_list.append(partition['device'])
			for device in device_list:
				self.owner.command('remove.storage.partition', [
						appliance_name,
						'scope=appliance',
						f'device={device}'
				])

			for partition in appliance['partition']:
				try:
					self.owner.log.info('adding appliance partition...')
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

					self.owner.command('add.storage.partition', parameters)
					self.owner.log.info(f'success adding appliance partition {partition}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding appliance partition: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding appliance partition: {e}')
						self.owner.errors += 1


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
				try:
					self.owner.log.info('adding appliance controller...')

					self.owner.command('add.storage.controller', parameters)

					self.owner.log.info(f'success adding appliance controller {controller}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding appliance controller: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding appliance controller: {e}')
						self.owner.errors += 1

