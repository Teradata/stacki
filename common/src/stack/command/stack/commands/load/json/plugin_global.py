# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'global'
	def requires(self):
		return [ 'software', 'host', 'network', 'group', 'appliance', 'os', 'environment', 'bootaction' ]

	def run(self, args):

		#check if the user would like to import global data
		if args and 'global' not in args:
			return

		#self.owner.data contains the data from the json file defined in init
		if 'global' in self.owner.data:
			import_data = self.owner.data['global']
		else:
			print('no global data in json file')
			return

		for scope in import_data:
			#check to make sure the scope is valid
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
									f'shadow={attr_shadow}' ])
						print(f'success setting global attr {attr["attr"]}')
						self.owner.successes += 1

					except Exception as e:
						if 'exists' in str(e):
							print(f'warning setting global attr {attr["attr"]}: {e}')
							self.owner.warnings += 1
						else:
							print(f'error setting global attr {attr["attr"]}: {e}')
							self.owner.errors += 1


			elif scope == 'route':
				for route in import_data[scope]:
					try:
						self.owner.command('add.route', [
									f'address={route["network"]}',
									f'gateway={route["gateway"]}',
									f'netmask={route["netmask"]}'])
						print(f'success adding global route {route["network"]}')
						self.owner.successes += 1

					except Exception as e:
						if 'exists' in str(e):
							print(f'warning adding global route {route["network"]}: {e}')
							self.owner.warnings += 1
						else:
							print(f'error adding global route {route["network"]}: {e}')
							self.owner.errors += 1

			elif scope == 'firewall':
				for rule in import_data[scope]:
					try:
						self.owner.command('add.firewall', [
									f'action={rule["action"]}',
									f'chain={rule["chain"]}',
									f'protocol={rule["protocol"]}',
									f'service={rule["service"]}',
									f'network={rule["network"]}',
									f'output-network={rule["output-network"]}',
									f'rulename={rule["name"]}',
									f'table={rule["table"]}' ])
						print(f'success adding global firewall fule {rule["name"]}')
						self.owner.successes += 1

					except Exception as e:
						if 'exists' in str(e):
							print(f'warning adding global firewall rule {rule["name"]}: {e}')
							self.owner.warnings += 1
						else:
							print(f'error adding global firewall rule {rule["name"]}: {e}')
							self.owner.errors += 1

			elif scope == 'partition':
				for partition in import_data[scope]:
					try:
						# normally the scope would be the first argument but since we are in the global plugin we need to leave it blank. Stacki defaults to global
						self.owner.command('add.storage.partition', [
									f'device={partition["device"]}',
									f'options={partition["options"]}',
									f'mountpoint={partition["mountpoint"]}',
									f'partid={partition["partid"]}',
									f'size={partition["size"]}',
									f'type={partition["fstype"]}',
									])
						print(f'success adding global partition {partition["device"]}')
						self.owner.successes += 1

					except Exception as e:
						if 'exists' in str(e):
							print(f'warning adding global partition {partition["device"]} {partition["mountpoint"]}: {e}')
							self.owner.warnings += 1
						else:
							print(f'error adding global partition {partition["device"]} {partition["mountpoint"]}: {e}')
							self.owner.errors += 1

			elif scope == 'controller':
				for controller in import_data[scope]:
					command = [f'arrayid={controller["arrayid"]}',
							f'raidlevel={controller["raidlevel"]}',
							f'slot={controller["slot"]}',
							]
					if controller['adapter']:
						command.append(controller['adapter'])
					if controller['enclosure']:
						command.append(controller['enclosure'])

					# is controller['scope'] unused in the add?
					# is controller['options'] unused in the add?
					try:
						self.owner.command('add.storage.controller', command)
						print(f'success adding global controller {controller["arrayid"]}')
						self.owner.successes += 1

					except Exception as e:
						if 'exists' in str(e):
							print(f'warning adding global controller: {e}')
							self.owner.warnings += 1
						else:
							print(f'error adding global controller: {e}')
							self.owner.errors += 1

			else:
				print(f'error potentially invalid entry in json. {scope} is not a valid gloabl scope')

