# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'os'

	def run(self, args):
	
		#check if the user would like to import os data
		#if there are no args, assume the user would like to import everthing
		if args and 'os' not in args:
			return

		#self.owner.data contains the data from the json file defined in init
		#check if there is any os data in the import file
		if 'os' in self.owner.data:
			import_data = self.owner.data['os']
		else:
			print('no os data in json file')
			return

		for os in import_data:
			os_name= os['name']
			
			for attr in os['attrs']:
				#determine if this is a shadow attr by looking at the type
				if attr['type'] == 'shadow':
					attr_shadow = True
				else:
					attr_shadow = False 
				try:
					self.owner.command('add.os.attr', [ os_name, f'attr={attr["attr"]}', f'value={attr["value"]}', f'shadow={attr_shadow}' ])
				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding os attr {attr}: {e}')
					else:
						print(f'error adding os attr {attr}: {e}')

			for route in os['route']:
				try:
					self.owner.command('add.os.route', [ os_name, f'address={route["network"]}', f'gateway={route["gateway"]}', f'netmask={route["netmask"]}' ])
				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding os route {route}: {e}')
					else:
						print(f'error adding os route {route}: {e}')


			for rule in os['firewall']:
				try:
					self.owner.command('add.os.firewall', [ os_name, f'action={rule["action"]}', f'chain={rule["chain"]}', f'protocol={rule["protocol"]}', f'service={rule["service"]}', f'network={rule["network"]}', f'output-network={rule["output_network"]}', f'rulename={rule["name"]}', f'table={rule["table"]}' ])
				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding os firewall rule {rule}: {e}')
					else:
						print(f'error adding os firewall rule {rule}: {e}')


			for partition in os['partition']:
				print('adding partition...')
				try:
					self.owner.command('add.storage.partition', [ os_name, f'device={partition["device"]}', f'options={partition["options"]}', f'mountpoint={partition["mountpoint"]}', f'partid={partition["partid"]}', f'size={partition["size"]}', f'type={partition["fstype"]}' ])
				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding partition {partition}: {e}')
					else:
						print(f'error adding partition {partition}: {e}')


			for controller in os['controller']:
				print ('adding controller...')
				try:
					#hotspare is an option in stack add storage controller, however there is no database column
					#for it in storage_controller and it is not listed in stack list storage controller
					#f'hotspare={controller["hotspare"]}'
					self.owner.command('add.storage.controller', [ os_name, f'adapter={controller["adapter"]}', f'arrayid={controller["arrayid"]}', f'enclosure={controller["enclosure"]}', f'raidlevel={controller["raidlevel"]}', f'slot={controller["slot"]}' ])
				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding os controller {controller}: {e}')
					else:
						print(f'error adding os controller {controller}: {e}')

RollName = "stacki"
