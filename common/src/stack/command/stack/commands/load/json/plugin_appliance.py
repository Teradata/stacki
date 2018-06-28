# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'appliance'

	def run(self, args):

		if args and 'appliance' not in args:
			return

		#check if the user would like to load appliance data
		if 'appliance' in self.owner.data:
			import_data = self.owner.data['appliance']
		else:
			print('no appliance data in json file')
			return
	
		#add each appliance then assign its various values to it
		for appliance in import_data:
			appliance_name = appliance['name']
			try:
				self.owner.command('add.appliance', [ appliance_name ])
				print(f'success adding appliance {appliance_name}')
				self.owner.successes += 1

			except Exception as e:
				if 'exists' in str(e):
					print(f'warning adding appliance {appliance_name}: {e}')
					self.owner.warnings += 1
				else:
					print(f'error adding appliance {appliance_name}: {e}')	
					self.owner.errors += 1

			for attr in appliance['attrs']:
				try:
					if attr['type'] == 'shadow':
						self.owner.command('add.appliance.attr', [ appliance_name, 
									f'attr={attr["attr"]}', 
									f'value={attr["value"]}', 
									'shadow=True' ])
					else:
						self.owner.command('add.appliance.attr', [ appliance_name, 
									f'attr={attr["attr"]}', 
									f'value={attr["value"]}' ])
					print(f'success adding appliance attr {attr["attr"]}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding appliance attr {attr["attr"]}: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding appliance attr {attr["attr"]}: {e}')
						self.owner.errors += 1
	
			for route in appliance['route']:
				try:
					self.owner.command('add.appliance.route', [ appliance_name, 
								f'address={route["network"]}', 
								f'gateway={route["gateway"]}', 
								f'netmask={route["netmask"]}' ])
					print(f'success adding appliance route {route}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding appliance route: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding appliance route: {e}')
						self.owner.errors += 1

			for rule in appliance['firewall']:
				try:
					self.owner.command('add.appliance.firewall', [ appliance_name, 
								f'action={rule["action"]}', 
								f'chain={rule["chain"]}', 
								f'protocol={rule["protocol"]}', 
								f'service={rule["service"]}', 
								f'network={rule["network"]}', 
								f'output-network={rule["output-network"]}', 
								f'rulename={rule["name"]}', 
								f'table={rule["table"]}' ])
					print(f'success adding appliance firewall rule {rule}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding appliance firewall rule {rule["name"]}: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding appliance firewall rule {rule["name"]}: {e}')
						self.owner.errors += 1


			for partition in appliance['partition']:
				try:
					print('adding appliance partition...')
					self.owner.command('add.storage.partition', [ appliance_name, 
								f'device={partition["device"]}', 
								f'options={partition["options"]}', 
								f'mountpoint={partition["mountpoint"]}', 
								f'partid={partition["partid"]}', 
								f'size={partition["size"]}', 
								f'type={partition["fstype"]}' ])
					print(f'success adding appliance partition {partition}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding appliance partition: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding appliance partition: {e}')
						self.owner.errors += 1


			for controller in appliance['controller']:
				command = [appliance_name, 
						f'arrayid={controller["arrayid"]}',
						f'raidlevel={controller["raidlevel"]}',
						f'slot={controller["slot"]}' ]
				if controller['adapter']:
					command.append(f'adapter={controller["adapter"]}')
				if controller['enclosure']:
					command.append(f'enclosure={controller["enclosure"]}')
				if controller['options']:
					command.append(f'options={controller["options"]}')
				try:
					print('adding appliance controller...')

					self.owner.command('add.storage.controller', command) 

					print(f'success adding appliance controller {controller}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding appliance ontroller: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding appliance ontroller: {e}')
						self.owner.errors += 1

