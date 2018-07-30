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
		return [ 'software', 'environment', 'group', 'network', 'appliance', 'os', 'global' ]

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
			try:
				parameters = [
					host_name,
					f'box={host["box"]}',
					f'longname={host["appliancelongname"]}',
					f'rack={host["rack"]}',
					f'rank={host["rank"]}'
				]
				if host['environment']:
					parameters.append(f'environment={host["environment"]}')
				self.owner.command('add.host', parameters)

				self.owner.log.info(f'success adding host {host["name"]}')
				self.owner.successes += 1

			except CommandError as e:
				if 'exists' in str(e):
					self.owner.log.info(f'warning adding host {host["name"]}: {e}')
					self.owner.warnings += 1
				else:
					self.owner.log.info(f'error adding host {host["name"]}: {e}')
					self.owner.errors += 1


			# iterate through each interface for the host and set it
			for interface in host['interface']:
				try:
					self.owner.command('add.host.interface', [host_name, f'interface={interface["interface"]}' ])
					self.owner.log.info(f'success adding interface {interface["interface"]}')
					self.owner.successes += 1
				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding interface {interface["interface"]}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding interface {interface["interface"]}: {e}')
						self.owner.errors += 1


				# iterate over each key in interface, ignoring 'already exists' warnings
				for interface in host['interface']:
					for k, v in interface.items():
						if v and k != 'interface' and k!= 'alias':
							try:
								self.owner.command(f'set.host.interface.{k}', [
													host_name,
													f'{k}={v}',
													f'interface={interface["interface"]}',
								])
							except CommandError as e:
								if 'exists' in str(e):
									self.owner.log.info(f'warning setting {host_name} interface {k}')
									self.owner.warnings += 1
								else:
									self.owner.log.info(f'error setting {host_name} interface {k}: {e}')
									self.owner.errors += 1
					# the alias cannot be set, so add it here. There can be multiple
					for alias in interface['alias']:
						try:
							self.owner.command('add.host.alias', [
											host_name,
											f'alias={alias["alias"]}',
											f'interface={interface["interface"]}',
							])
						except CommandError as e:
							if 'exists' in str(e):
								self.owner.log.info(f'warning adding {host_name} alias {alias}')
								self.owner.warnings += 1
							else:
								self.owner.log.info(f'error adding {host_name} alias {alias}: {e}')
								self.owner.errors += 1


			# iterate through each attr for the host and add it
			for attr in host['attrs']:
				attr_name = attr['name']
				attr_value = attr['value']
				if not isinstance(attr_value, str):
					attr_value = ' '.join(attr['value'])
				attr_shadow = attr['shadow']
				try:
					self.owner.command('set.host.attr', [
									host_name,
									f'attr={attr_name}',
									f'value={attr_value}',
									f'shadow={attr_shadow}'
					])
					self.owner.log.info(f'success setting {host["name"]} attr {attr_name}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning setting {host["name"]} attr {attr_name}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error setting {host["name"]} attr {attr_name}: {e}')
						self.owner.errors += 1

			#iterate through each firewall rule and add it
			for rule in host['firewall']:
				try:
					self.owner.command('add.host.firewall', [
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
									f'table={rule["table"]}'
					])
					self.owner.log.info(f'success adding host firewall rule {rule["name"]}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info (f'warning adding host firewall rule {rule["name"]}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info (f'error adding host firewall rule {rule["name"]}: {e}')
						self.owner.errors += 1



			for route in host['route']:
				try:
					self.owner.command('add.host.route', [
									host_name,
									f'address={route["network"]}',
									f'gateway={route["gateway"]}',
									f'netmask={route["netmask"]}'
					])
					self.owner.log.info(f'success adding host route {route}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding route {route["network"]}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding route {route["network"]}: {e}')
						self.owner.errors += 1

			for group in host['group']:
				try:
					self.owner.command('add.host.group', [
									host_name,
									f'group={group}'
					])
				except CommandError as e:
					if 'already' in str(e):
						self.owner.log.info(f'warning adding host {host_name} to group {group}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding host {host_name} to group {group}')
						self.owner.errors += 1


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
				try:
					self.owner.command('add.storage.partition', parameters)
					self.owner.log.info(f'success adding partition {partition}')
					self.owner.successes += 1


#def something(func, params, logger, msg):
#def something(cmd_string, params, message):
#	try:
#		func(params)
#		logger.info
#	except:
#		if exists:
#			logger.warnings
#		else
#			logger.error

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info (f'warning adding partition: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info (f'error adding partition: {e}')
						self.owner.errors += 1



			for controller in host['controller']:
				parameters = [
					host_name,
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


				try:
					self.owner.log.info('adding host controller...')
					self.owner.command('add.storage.controller', parameters)
					self.owner.log.info(f'success adding host controller {controller}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding host ontroller: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding host controller: {e}')
						self.owner.errors += 1



			# set the installaction of the host
			try:
				self.owner.command('set.host.installaction', [
							host_name,
							f'action={host["installaction"]}' ])

				self.owner.log.info(f'success setting installaction of {host_name} to {host["installaction"]}')
				self.owner.successes += 1

			except CommandError as e:
				if 'exists' in str(e):
					self.owner.log.info(f'warning setting installaction of {host_name} to "{host["installaction"]}": {e}')
					self.owner.warnings += 1
				else:
					self.owner.log.info(f'error setting installaction of {host_name} to "{host["installaction"]}": {e}')
					self.owner.errors += 1


			#set metadata if there is any
			if host['metadata']:
				try:
					self.owner.command('set.host.metadata', [ host_name, f'metadata={host["metadata"]}' ])
					self.owner.log.info(f'success setting metadata of {host_name}')
					self.owner.successes += 1
				except CommandError as e:
					self.owner.log.info(f'error setting metadata of {host_name}')
					self.owner.errors += 1

			#set the comment if there is one
			if host['comment']:
				try:
					self.owner.command('set.host.comment', [ host_name, f'comment={host["comment"]}' ])
					self.owner.log.info(f'success setting comment of {host_name}')
					self.owner.successes += 1
				except CommandError as e:
					self.owner.log.info(f'error setting comment of {host_name}')
					self.owner.errors += 1

			# set the environment if there is one
			if host['environment']:
				try:
					self.owner.command('set.host.environment', [ host_name, f'environment={host["environment"]}' ])
					self.owner.log.info(f'success setting environment of {host_name}')
					self.owner.successes += 1
				except CommandError as e:
					self.owner.log.info(f'error setting environment of {host_name} {e}')
					self.owner.errors += 1
