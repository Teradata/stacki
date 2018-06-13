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


	def run(self, args):
		
	
		#check if the user would like to import global data
		if args:
			if 'global' not in args:
				return

		#self.owner.data contains the data from the json file defined in init
		for item in self.owner.data:
			if item == 'global':
				import_data = self.owner.data[item]
			else:
				print('error no global data in json file')


		for scope in import_data:
			#check to make sure the scope is valid
			if scope == 'attrs':
				for attr in import_data[scope]:
# not needed				attr_scope = item['scope']
					attr_type = attr['type']

					if attr_type == 'shadow':
						attr_shadow = True
					else:
						attr_shadow = False

					attr_attr = attr['attr']
					attr_value = attr['value']
					try:
						self.owner.command('add.attr', [f'attr={attr_attr}', f'value={attr_value}', f'shadow={attr_shadow}' ])

					except Exception as e:
						print(f'error adding attr {attr_attr}: {e}')


			elif scope == 'route':
				for route in import_data[scope]:
					route_network = route['network']
					route_netmask = route['netmask']
					route_gateway = route['gateway']
					try:
						self.owner.command('add.route', [ f'address={route_network}', f'gateway={route_gateway}', f'netmask={route_netmask}'])
					except Exception as e:
						print(f'error adding route {route_network}: {e}')


			elif scope == 'firewall':
				for rule in import_data[scope]:
					rule_name = rule['name']
					rule_table = rule['table']
					rule_service = rule['service']
					rule_protocol = rule['protocol']
					rule_chain = rule['chain']
					rule_action = rule['action']
					rule_network = rule['network']
					rule_output_network = rule['output-network']
					rule_flags = rule['flags']
					rule_comment = rule['comment']
					rule_source = rule['source']
					rule_type = rule['type']
					try:
						self.owner.command('add.firewall', [ f'action={rule_action}', f'chain={rule_chain}', f'protocol={rule_protocol}', f'service={rule_service}', f'network={rule_network}', f'output-network={rule_output_network}', f'rulename={rule_name}', f'table={rule_table}' ])
					except Exception as e:
						print(f'error adding firewall rule {rule_name}: {e}')


			elif scope == 'partition':
				for partition in import_data[scope]:
					
				#	partition_scope = partition['scope']  # since we are in the global plugin the scope will always be global
					partition_device = partition['device']
					partition_options = partition['options']
					partition_mountpoint = partition['mountpoint']
					partition_partid = partition['partid']
					partition_size = partition['size']
					partition_type = partition['fstype']
					try:
						self.owner.command('add.storage.partition', [ f'device={partition_device}', f'options={partition_options}', f'mountpoint={partition_mountpoint}', f'partid={partition_partid}', f'size={partition_size}', f'type={partition_size}' ])  # normally the scope would be the first argument but since we are in the global plugin we need to leave it blank. It defaults to global
					except Exception as e:
						print(f'error adding partition {partition_device} {partition_mountpoint}: {e}')

	
			elif scope == 'controller':
				for controller in import_data[scope]:
				
					controller_scope = controller['scope']
					controller_enclosure = controller['enclosure']
					controller_adapter = controller['adapter']
					controller_slot = controller['slot']
					controller_raidlevel = controller['raidlevel']
					controller_arrayid = controller['arrayid']
					controller_options = controller['options']
					try:
						if controller_adapter and controller_enlosure:
							self.owner.command('add.storage.controller', [ f'adapter={controller_adapter}', f'arrayid={controller_arrayid}', f'enclosure={controller_enclosure}', f'raidlevel={controller_raidlevel}', f'slot={controller_slot}' ])
						elif not controller_adapter and controller_enclosure:
							self.owner.command('add.storage.controller', [ f'arrayid={controller_arrayid}', f'enclosure={controller_enclosure}', f'raidlevel={controller_raidlevel}', f'slot={controller_slot}' ])
						elif controller_adapter and not controller_enclosure:
							self.owner.command('add.storage.controller', [ f'adapter={controller_adapter}', f'arrayid={controller_arrayid}', f'raidlevel={controller_raidlevel}', f'slot={controller_slot}' ])
						else: 
							self.owner.command('add.storage.controller', [ f'arrayid={controller_arrayid}', f'raidlevel={controller_raidlevel}', f'slot={controller_slot}' ])


					except Exception as e:
						print(f'error adding controller: {e}')


			else:
				print(f'error potentially invalid entry in json. {scope} is not a valid gloabl scope')

RollName = "stacki"
