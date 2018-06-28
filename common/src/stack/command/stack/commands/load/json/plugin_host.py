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
				#the add command asks for 'longname'
				#the list command provides the 'appliance'
				#the only difference is that the first letter is uppercase
				longname = host['appliance'].title()
				if host['environment']:
					self.owner.command('add.host', [ host_name, 
								f'box={host["box"]}', 
								f'environment={host["environment"]}',
								f'longname={longname}', 
								f'rack={host["rack"]}', 
								f'rank={host["rank"]}' ])
				else:
					self.owner.command('add.host', [ host_name, 
								f'box={host["box"]}', 
								f'longname={longname}',
								f'rack={host["rack"]}', 
								f'rank={host["rank"]}' ])
				print(f'success adding host {host["name"]}')
				self.owner.successes += 1

			except Exception as e:
				if 'exists' in str(e):
					print(f'warning adding host {host["name"]}: {e}')
					self.owner.warnings += 1
				else:
					print(f'error adding host {host["name"]}: {e}')
					self.owner.errors += 1


			#iterate through each interface for the host and add it
			for interface in host['interface']:
				try:
					self.owner.command('add.host.interface', [ host_name, 
								f'interface={interface["name"]}', 
								f'ip={interface["ip"]}', 
								f'mac={interface["mac"]}', 
								f'network={interface["network"]}' ])
					print(f'success adding interface {interface["name"]}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding host interface {interface["name"]}: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding host interface {interface["name"]}: {e}')
						self.owner.errors += 1



			#iterate through each attr for the host and add it
			#this is broken come back ad fix it
			for attr in host['attrs']:
				attr_name = attr['name']
				attr_value = attr['value']  # this may pose a problem because the pallets and carts attrs have lists here. Need to investigate
				attr_shadow = attr['shadow']  # this will cause a problem if it is pasing a string rather than a bool. may need to resolve
				try:
					self.owner.command('add.host.attr', [ host_name, 
										f'attr={attr_name}', 
										f'value={attr_value}', 
										f'shadow={attr_shadow}' ])
					print(f'success adding host attr {attr_name}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding host attr {attr_name}: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding host attr {attr_name}: {e}')
						self.owner.errors += 1

			#iterate through each firewall rule and add it
			for rule in host['firewall']:
				try:
					#this will likely have an issue with service as it is a comma delimeted string that should be a list
					#need to come back and fix this
					#same thing with flags
					self.owner.command('add.host.firewall', [ host_name, 
								f'action={rule["action"]}', 
								f'chain={rule["chain"]}', 
								f'protocol={rule["protocol"]}', 
								f'service={rule["service"]}', 
								f'comment={rule["comment"]}', 
								f'flags={rule["flags"]}',  
								f'network={rule["network"]}', 
								f'output-netork={rule["output-network"]}', 
								f'rulename={rule["name"]}', 
								f'table={rule["table"]}' ])
					print(f'success adding host firewall rule {rule["name"]}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print (f'warning adding host firewall rule {rule["name"]}: {e}')
						self.owner.warnings += 1
					else:
						print (f'error adding host firewall rule {rule["name"]}: {e}')
						self.owner.errors += 1



			for route in host['route']:
				try:
					self.owner.command('add.host.route', [ host_name, 
								f'address={route["network"]}', 
								f'gateway={route["gateway"]}', 
								f'netmask={route["netmask"]}' ])
					print(f'success adding host route {route}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding route {route["network"]}: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding route {route["network"]}: {e}')
						self.owner.errors += 1


			for group in host['group']:
				#need to figure out how to deal with groups
				slef.owner.errors += 1
				print('todo')



			#this may not work if fstype is missing, need to do some more research
			for partition in host['partition']:
				try:
					if partition['fstype'] and partition['partid']:
						self.owner.command('add.host.partition', [ 
									host_name, 
									f'device={partition["device"]}', 
									f'fs={partition["fstype"]}', 
									f'mountpoint={partition["mountpoint"]}', 
									f'partid={partition["partid"]}', 
									f'size={partition["size"]}' ])
					elif partition['fstype'] and not partition['partid']:
						self.owner.command('add.host.partition', [ 
									host_name, 
									f'device={partition["device"]}', 
									f'fs={partition["fstype"]}', 
									f'mountpoint={partition["mountpoint"]}', 
									f'size={partition["size"]}' ])
					elif not partition['fstype'] and partition['partid']:
						self.owner.command('add.host.partition', [ 
									host_name, 
									f'device={partition["device"]}', 
									f'mountpoint={partition["mountpoint"]}', 
									f'partid={partition["partid"]}', 
									f'size={partition["size"]}' ])
					else:
						self.owner.command('add.host.partition', [ 
									host_name, 
									f'device={partition["device"]}', 
									f'mountpoint={partition["mountpoint"]}', 
									f'size={partition["size"]}' ])
					print(f'success adding partition {partition}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print (f'warning adding partition: {e}')
						self.owner.warnings += 1
					else:
						print (f'error adding partition: {e}')
						self.owner.errors += 1


	
			for controller in host['controller']:
				#this will end up being the same thing 
				self.owner.errors += 1
				print('todo')

			#set the installaction of the host
			try:
				self.owner.command('set.host.installaction', [
							host_name,
							f'action={host["installaction"]}' ])

				print(f'success setting installaction of {host_name} to {host["installaction"]}')
				self.owner.successes += 1

			except Exception as e:
				if 'exists' in str(e):
					print(f'warning setting installaction of {host_name} to "{host["installaction"]}": {e}')
					self.owner.warnings += 1
				else:
					print(f'error setting installaction of {host_name} to "{host["installaction"]}": {e}')
					self.owner.errors += 1

