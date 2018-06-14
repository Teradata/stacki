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
			except Exception as e:
				print(f'error adding appliance {appliance_name}: {e}')
	
			for attr in appliance['attrs']:
				try:
					if attr['type'] == 'shadow':
						self.owner.command('add.appliance.attr', [ appliance_name, f'attr={attr["attr"]}', f'value={attr["value"]}', 'shadow=True' ])
					else:
						self.owner.command('add.appliance.attr', [ appliance_name, f'attr={attr["attr"]}', f'value={attr["value"]}' ])
				except Exception as e:
					print(f'error adding appliance attr {attr["attr"]}: {e}')
	
			for route in appliance['route']:
				try:
					self.owner.command('add.appliance.route', [ appliance_name, f'address={route["network"]}', f'gateway={route["gateway"]}', f'netmask={route["netmask"]}' ])
				except Exception as e:
					print(f'error adding appliance route: {e}')

			for rule in appliance['firewall']:
				try:
					self.owner.command('add.appliance.firewall', [ appliance_name, f'action={rule["action"]}', f'chain={rule["chain"]}', f'protocol={rule["protocol"]}', f'service={rule["service"]}', f'netowrk={rule["network"]}', f'output-network={rule["output-network"]}', f'rulename={rule["name"]}', f'table={rule["table"]}' ])
				except Exception as e:
					print(f'error adding appliance firewall rule {rule["name"]}: {e}')


			for partition in appliance['partition']:
				try:
					print('adding appliance partition...')
					self.owner.command('add.storage.partition', [ appliance_name, f'device={partition["device"]}', f'options={partition["options"]}', f'mountpoint={partition["mountpoint"]}', f'partid={partition["partid"]}', f'size={partition["size"]}', f'type={partition["fstype"]}' ])
				except Exception as e:
					print(f'error adding appliance partition: {e}')

			for controller in appliance['controller']:
				try:
					print('adding appliance controller...')
					self.owner.command('add.storage.controller', [ appliance_name, f'adapter={controller["adapter"]}', f'arrayid={controller["arrayid"]}', f'enclosure={controller["enclosure"]}', f'raidlevel={controller["raidlevel"]}', f'slot={controller["slot"]}' ])
				except Exception as e:
					print(f'error adding appliance ontroller: {e}')




