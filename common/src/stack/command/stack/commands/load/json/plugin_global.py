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

		self.notify('\n\tLoading global\n')
		for scope in import_data:
			# check to make sure the scope is valid
			if scope == 'attrs':
				for attr in import_data[scope]:
					attr_type = attr['type']

					if attr_type == 'shadow':
						attr_shadow = True
					else:
						attr_shadow = False

					try:
						self.owner.command('set.attr', [
								f'attr={attr["attr"]}',
								f'value={attr["value"]}',
								f'shadow={attr_shadow}'
						])
						self.owner.log.info(f'success setting global attr {attr["attr"]}')
						self.owner.successes += 1

					except CommandError as e:
						if 'exists' in str(e):
							self.owner.log.info(f'warning setting global attr {attr["attr"]}: {e}')
							self.owner.warnings += 1
						else:
							self.owner.log.info(f'error setting global attr {attr["attr"]}: {e}')
							self.owner.errors += 1


			elif scope == 'route':
				for route in import_data[scope]:
					try:
						self.owner.command('add.route', [
								f'address={route["network"]}',
								f'gateway={route["gateway"]}',
								f'netmask={route["netmask"]}'
						])
						self.owner.log.info(f'success adding global route {route["network"]}')
						self.owner.successes += 1

					except CommandError as e:
						if 'exists' in str(e):
							self.owner.log.info(f'warning adding global route {route["network"]}: {e}')
							self.owner.warnings += 1
						else:
							self.owner.log.info(f'error adding global route {route["network"]}: {e}')
							self.owner.errors += 1

			elif scope == 'firewall':
				for rule in import_data[scope]:
					try:
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
						self.owner.command('add.firewall', parameters)
						self.owner.log.info(f'success adding global firewall fule {rule["name"]}')
						self.owner.successes += 1

					except CommandError as e:
						if 'exists' in str(e):
							# the firewall rule exists but we want to replace it
							try:
								self.owner.command('remove.firewall', [ f'rulename={rule["name"]}' ])
								self.owner.command('add.firewall', parameters)
								self.owner.log.info(f'success replacing global firewall rule {rule["name"]}')
								self.owner.successes += 1
							except CommandError as e:
								self.owner.log.info(f'error adding global firewall rule {rule["name"]}: {e}')
								self.owner.errors += 1
						else:
							self.owner.log.info(f'error adding global firewall rule {rule["name"]}: {e}')
							self.owner.errors += 1

			elif scope == 'partition':
				for partition in import_data[scope]:
					try:
						self.owner.log.info('adding global partition...')
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

						self.owner.command('add.storage.partition', parameters)
						self.owner.log.info(f'success adding global partition {partition}')
						self.owner.successes += 1

					except CommandError as e:
						if 'exists' in str(e):
							self.owner.log.info(f'warning adding global partition: {e}')
							self.owner.warnings += 1
						else:
							self.owner.log.info(f'error adding global partition: {e}')
							self.owner.errors += 1


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

					# is controller['scope'] unused in the add?
					# is controller['options'] unused in the add?
					try:
						self.owner.command('add.storage.controller', parameters)
						self.owner.log.info(f'success adding global controller {controller["arrayid"]}')
						self.owner.successes += 1

					except CommandError as e:
						if 'exists' in str(e):
							self.owner.log.info(f'warning adding global controller: {e}')
							self.owner.warnings += 1
						else:
							self.owner.log.info(f'error adding global controller: {e}')
							self.owner.errors += 1

			else:
				self.owner.log.info(f'error potentially invalid entry in json. {scope} is not a valid gloabl scope')
