# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'host'

	def run(self, args):
	
		#check if the user would like to import host data
		#if there are no args, assume the user would like to import everthing
		if args and 'host' not in args:
			return

		#self.owner.data contains the data from the json file defined in init
		#check if there is any host data before we go getting all kinds of key errors
		if 'host' in self.owner.data:
			import_data = self.owner.data['host']
		else:
			print('no host data in json file')
			return

		#add each host then assign its various values to it
		for host in import_data:
			host_name = host['name']
			try:
				if host['environment:']:
					self.owner.command('add.host', [ host_name, f'box={host["box"]}', f'environment={host["environment"]}', f'rack={host["rack"]}', f'rank={host["rank"]}' ])
				else:
					self.owner.command('add.host', [ host_name, f'box={host["box"]}', f'rack={host["rack"]}', f'rank={host["rank"]}' ])

			except Exception as e:
				print(f'error adding host {host["name"]}: {e}')

			#iterate through each interface for the host and add it
			for interface in host['interface']:
				try:
					self.owner.command('add.host.interface', [ host_name, f'interface={interface["name"]}', f'ip={interface["ip"]}', f'mac={interface["mac"]}', f'network={interface["network"]}' ]) 
				except Exception as e:
					print(f'error adding interface {interface["name"]}: {e}')

			#iterate through each attr for the host and add it
			#this is broken come back ad fix it
			for attr in host['attrs']:
				attr_name = attr['name']
				attr_value = attr['value']  # this may pose a problem because the pallets and carts attrs have lists here. Need to investigate
				attr_shadow = attr['shadow']  # this will cause a problem if it is pasing a string rather than a bool. may need to resolve
				try:
					self.owner.command('add.host.attr', [ host_name, f'attr={attr_name}', f'value={attr_value}', f'shadow={attr_shadow}' ])
				except Exception as e:
					print(f'error adding attr {attr_name}: {e}')


			#iterate through each firewall rule and add it
			for rule in host['firewall']:
				try:
					#this will likely have an issue with service as it is a comma delimeted string that should be a list
					#need to come back and fix this
					#same thing with flags
					self.owner.command('add.host.firewall', [ host_name, f'action={rule["action"]}', f'chain={rule["chain"]}', f'protocol={rule["protocol"]}', f'service={rule["service"]}', f'coment={rule["comment"]}', f'flags={rule["flags"]}',  f'network={rule["network"]}', f'output-netork={rule["output-network"]}', f'rulename={rule["name"]}', f'table={rule["table"]}' ])

				except Exception as e:
					print (f'error adding host firewall rule {rule["name"]}: {e}')

			for route in host['route']:
				try:
					self.owner.command('add.host.route', [ host_name, f'address={route["network"]}', f'gateway={route["gateway"]}', f'netmask={route["netmask"]}' ]) 
				except Exception as e:
					print(f'error adding route {route["network"]}: {e}')


			for group in host['group']:
				#need to figure out how to deal with groups
				print('todo')



			#this may not work if fstype is missing, need to do some more research
			for partition in host['partition']:
				try:
					if partition['fstype'] and partition['partid']:
						self.owner.command('add.host.partition', [ host_name, f'device={partition["device"]}', f'fs={partition["fstype"]}', f'mountpoint={partition["mountpoint"]}', f'partid={partition["partid"]}', f'size={partition["size"]}' ])
					elif partition['fstype'] and not partition['partid']:
						self.owner.command('add.host.partition', [ host_name, f'device={partition["device"]}', f'fs={partition["fstype"]}', f'mountpoint={partition["mountpoint"]}', f'size={partition["size"]}' ])
					elif not partition['fstype'] and partition['partid']:
						self.owner.command('add.host.partition', [ host_name, f'device={partition["device"]}', f'mountpoint={partition["mountpoint"]}', f'partid={partition["partid"]}', f'size={partition["size"]}' ])
					else:
						self.owner.command('add.host.partition', [ host_name, f'device={partition["device"]}', f'mountpoint={partition["mountpoint"]}', f'size={partition["size"]}' ])
				except Exception as e:
					print (f'error adding partition: {e}')

	
			for controller in host['controller']:
				#this will end up being the same thing 
				print('todo')
RollName='Stacki'
		
