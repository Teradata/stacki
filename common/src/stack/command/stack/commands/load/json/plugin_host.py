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
				command = [ host_name,
						f'box={host["box"]}',
						f'longname={longname}',
						f'rack={host["rack"]}',
						f'rank={host["rank"]}' ]
				if host['environment']:
					command.append(f'environment={host["environment"]}')
				self.owner.command('add.host', command)

				print(f'success adding host {host["name"]}')
				self.owner.successes += 1

			except Exception as e:
				if 'exists' in str(e):
					print(f'warning adding host {host["name"]}: {e}')
					self.owner.warnings += 1
				else:
					print(f'error adding host {host["name"]}: {e}')
					self.owner.errors += 1


			#iterate through each interface for the host and set it
			for interface in host['interface']:
				try:

					if interface['default']:
						self.owner.command('set.host.interface.default', [ host_name,
													'default=True',
													f'interface={interface["interface"]}' ])
						print('success setting interface default')
						self.owner.successes += 1
					if interface['network']:
						self.owner.command('set.host.interface.network', [ host_name,
													f'network={interface["network"]}',
													f'interface={interface["interface"]}' ])
						print('success setting interface network')
						self.owner.successes += 1
					if interface['mac']:
						self.owner.command('set.host.interface.mac', [ host_name,
													f'mac={interface["mac"]}',
													f'interface={interface["interface"]}' ])
						print('success setting interface mac')
						self.owner.successes += 1
					if interface['ip']:
						self.owner.command('set.host.interface.ip', [ host_name,
													f'ip={interface["ip"]}',
													f'interface={interface["interface"]}' ])
						print('success setting interface ip')
						self.owner.successes += 1
					if interface['name']:
						self.owner.command('set.host.interface.name', [ host_name,
													f'name={interface["name"]}',
													f'interface={interface["interface"]}' ])
						print('success setting interface name')
						self.owner.successes += 1
					if interface['module']:
						self.owner.command('set.host.interface.module', [ host_name,
													f'module={interface["module"]}',
													f'interface={interface["interface"]}' ])
						print('success setting interface module')
						self.owner.successes += 1
					if interface['vlan']:
						self.owner.command('set.host.interface.vlan', [ host_name,
													f'vlan={interface["vlan"]}',
													f'interface={interface["interface"]}' ])
						print('success setting interface vlan')
						self.owner.successes += 1
					if interface['options']:
						self.owner.command('set.host.interface.options', [ host_name,
													f'options={interface["options"]}',
													f'interface={interface["interface"]}' ])
						print('success setting interface options')
						self.owner.successes += 1
					if interface['channel']:
						self.owner.command('set.host.interface.channel', [ host_name,
													f'channel={interface["channel"]}',
													f'interface={interface["interface"]}' ])
						print('success setting interface channel')
						self.owner.successes += 1


					print(f'success setting all interface attrs for {interface["name"]}')
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
				self.owner.errors += 1
				print('Error host group not yet supported')



			#this may not work if fstype is missing, need to do some more research
			for partition in host['partition']:
				command = [host_name,
						f'device={partition["device"]}',
						f'mountpoint={partition["mountpoint"]}',
						f'size={partition["size"]}']
				if partition['fstype']:
					command.append(f'fs={partition["fstype"]}')
				if partition['partid']:
					command.append(f'partid={partition["partid"]}')
				try:
					self.owner.command('add.host.partition', command)
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
				try:
					print('adding host controller...')
					self.owner.command('add.storage.controller', [ host_name,
								f'adapter={controller["adapter"]}',
								f'arrayid={controller["arrayid"]}',
								f'enclosure={controller["enclosure"]}',
								f'raidlevel={controller["raidlevel"]}',
								f'slot={controller["slot"]}' ])
					print(f'success adding host controller {controller}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning adding host ontroller: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding host controller: {e}')
						self.owner.errors += 1



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

