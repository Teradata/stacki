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
		return 'host'
	def requires(self):
		return [ 'software', 'environment', 'group', 'network', 'appliance', 'os', 'global', 'bootaction' ]

	def run(self, args):

		# check if the user would like to import host data
		# if there are no args, assume the user would like to import everthing
		if args and 'host' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'host' in self.owner.data:
			import_data = self.owner.data['host']
		else:
			self.owner.log.info('no host data in json file')
			return

		self.notify('\n\tLoading host\n')
		# add each host then assign its various values to it
		for host in import_data:
			host_name = host['name']
			parameters = [
				host_name,
				f'box={host["box"]}',
				f'rack={host["rack"]}',
				f'rank={host["rank"]}',
				f'appliance={host["appliance"]}'
			]
			if host['environment']:
				parameters.append(f'environment={host["environment"]}')
			self.owner.try_command('add.host',parameters , f'adding host {host["name"]}', 'exists')


			# iterate through each interface for the host and set it
			for interface in host['interface']:
				self.owner.try_command('add.host.interface',[ host_name, f'interface={interface["interface"]}'], f'adding interface {interface["interface"]}', 'exists')


				# iterate over each key in interface, ignoring 'already exists' warnings
			for interface in host['interface']:
				for k, v in interface.items():
					if v and k != 'interface' and k!= 'alias':
						parameters = [
							host_name,
							f'{k}={v}',
							f'interface={interface["interface"]}',
							]
						self.owner.try_command(f'set.host.interface.{k}', parameters, f'setting {host_name} interface {k}', 'exists')

				# the alias cannot be set, so add it here. There can be multiple
				for alias in interface['alias']:
					parameters = [
						host_name,
						f'alias={alias["alias"]}',
						f'interface={interface["interface"]}',
						]
					self.owner.try_command('add.host.alias', parameters, f'adding {host_name} alias {alias}', 'exists')

			# iterate through each attr for the host and add it
			for attr in host['attrs']:
				attr_name = attr['name']
				attr_value = attr['value']
				if not isinstance(attr_value, str):
					attr_value = ' '.join(attr['value'])
				attr_shadow = attr['shadow']
				parameters = [
					host_name,
					f'attr={attr_name}',
					f'value={attr_value}',
					f'shadow={attr_shadow}'
				]
				self.owner.try_command('set.host.attr', parameters, f'setting {host["name"]} attr {attr_name}', 'exists')

			# add firewall rules. If the firewall rule already exists, then remove it and add the one in the json
			for rule in host['firewall']:
				parameters = [
					host_name,
					f'action={rule["action"]}',
					f'chain={rule["chain"]}',
					f'protocol={rule["protocol"]}',
					f'service={rule["service"]}',
					f'comment={rule["comment"]}',
					f'flags={rule["flags"]}',
					f'network={rule["network"]}',
					f'output-network={rule["output-network"]}',
					f'rulename={rule["name"]}',
					f'table={rule["table"]}',
				]
				if rule['flags']:
					parameters.append(f'flags={rule["flags"]}')
				if rule['comment']:
					parameters.append(f'comment={rule["comment"]}')
				# if the add command returns false, run the remove command then re-run the add command
				if not self.owner.try_command('add.host.firewall', parameters, f'adding host firewall rule {rule["name"]}', 'exists'):
					self.owner.try_command('remove.host.firewall', [ host_name, f'rulename={rule["name"]}' ], 'removing host firewall rule {rule["action"]}', 'exists')
					self.owner.try_command('add.host.firewall', parameters, f'adding host firewall rule {rule["name"]}', 'exists')

			# add host routes
			for route in host['route']:
				parameters = [
					host_name,
					f'address={route["network"]}',
					f'gateway={route["gateway"]}',
					f'netmask={route["netmask"]}',
				]
				self.owner.try_command('add.host.route', parameters, f'adding host route {route}', 'exists')

			# add host groups
			for group in host['group']:
				parameters = [
					host_name,
					f'group={group}',
				]
				self.owner.try_command('add.host.group', parameters, f'adding host {host_name} to group {group}', 'exists')

			# add host partitions
			for partition in host['partition']:
				parameters = [
					host_name,
					f'device={partition["device"]}',
					f'mountpoint={partition["mountpoint"]}',
					f'size={partition["size"]}',
					]
				if partition['fstype']:
					parameters.append(f'fs={partition["fstype"]}')
				if partition['partid']:
					parameters.append(f'partid={partition["partid"]}')
				if partition['options']:
					parameters.append(f'options={partition["options"]}')
				self.owner.try_command('add.storage.partition', parameters, f'adding partition {partition}', 'exists')

			# add host controllers
			for controller in host['controller']:
				parameters = [
					host_name,
					f'scope={controller["scope"]}',
					f'arrayid={controller["arrayid"]}',
				]
				if controller['adapter']:
					parameters.append(f'adapter={controller["adapter"]}')
				if controller['enclosure']:
					parameters.append(f'enclosure={controller["enclosure"]}')
				if controller['raidlevel']:
					parameters.append(f'raidlevel={controller["raidlevel"]}')
				if controller['slot']:
					parameters.append(f'slot={controller["slot"]}')
				self.owner.try_command('add.storage.controller', parameters, f'adding host controller {controller}', 'exists')


			# set the installaction of the host
			parameters = [
				host_name,
				f'action={host["installaction"]}',
			]
			self.owner.try_command('set.host.installaction', parameters, f'setting installaction of {host_name} to {host["installaction"]}', 'exists')

			# set metadata if there is any
			if host['metadata']:
				parameters = [
					host_name,
					f'metadata={host["metadata"]}',
				]
				self.owner.try_command('set.host.metadata', parameters, f'setting metadata of {host_name}', 'exists')

			# set the comment if there is one
			if host['comment']:
				parameters = [
					host_name,
					f'comment={host["comment"]}',
				]
				self.owner.try_command('set.host.comment', parameters, f'setting comment of {host_name}', 'exists')

			# set the environment if there is one
			if host['environment']:
				parameters = [
					host_name,
					f'environment={host["environment"]}',
				]
				self.owner.try_command('set.host.environment', parameters, f'setting environment of {host_name}', 'exists')
