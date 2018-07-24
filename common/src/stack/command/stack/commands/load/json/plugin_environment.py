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
		return 'environment'
	def requires(self):
		return [ 'software' ]

	def run(self, args):

		# check if the user would like to import environment data
		# if there are no args, assume the user would like to import everthing
		if args and 'environment' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'environment' in self.owner.data:
			import_data = self.owner.data['environment']
		else:
			self.owner.log.info('no environment data in json file')
			return

		self.notify('\n\tLoading environment\n')
		for environment in import_data:
			environment_name= environment['name']
			try:
				self.owner.command('add.environment', [ environment_name ])
			except CommandError as e:
				if 'exists' in str(e):
					self.owner.log.info(f'warning adding environment {environment_name}: {e}')
					self.owner.warnings += 1
				else:
					self.owner.log.info(f'error adding environment {environment}: {e}')
					self.owner.errors += 1

			for attr in environment['attrs']:
				#determine if this is a shadow attr by looking at the type
				if attr['type'] == 'shadow':
					attr_shadow = True
				else:
					attr_shadow = False
				try:
					self.owner.command('add.environment.attr', [
							environment_name,
							f'attr={attr["attr"]}',
							f'value={attr["value"]}',
							f'shadow={attr_shadow}'
					])
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding environment attr {attr}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding environment attr {attr}: {e}')
						self.owner.errors += 1

			# none of the following have corresponding stack commands

#			for route in environment['route']:
#				try:
#					self.owner.command('add.environment.route', [ environment_name, f'address={route["network"]}', f'gateway={route["gateway"]}', f'netmask={route["netmask"]}' ])
#				except CommandError as e:
#					if 'exists' in str(e):
#						self.owner.log.info(f'warning adding environment route {route}: {e}')
#					else:
#						self.owner.log.info(f'error adding environment route {route}: {e}')


#			for rule in environment['firewall']:
#				try:
#					self.owner.command('add.environment.firewall', [ environment_name, f'action={rule["action"]}', f'chain={rule["chain"]}', f'protocol={rule["protocol"]}', f'service={rule["service"]}', f'network={rule["network"]}', f'output-network={rule["output_network"]}', f'rulename={rule["name"]}', f'table={rule["table"]}' ])
#				except CommandError as e:
#					if 'exists' in str(e):
#						self.owner.log.info(f'warning adding environment firewall rule {rule}: {e}')
#					else:
#						self.owner.log.info(f'error adding environment firewall rule {rule}: {e}')


#			for partition in environment['partition']:
#				self.owner.log.info('adding environment partition...')
#				try:
#					self.owner.command('add.storage.partition', [ environemnt_name, f'device={partition["device"]}', f'options={partition["options"]}', f'mountpoint={partition["mountpoint"]}', f'partid={partition["partid"]}', f'size={partition["size"]}', f'type={partition["fstype"]}' ])
#				except CommandError as e:
#					if 'exists' in str(e):
#						self.owner.log.info(f'warning adding environment partition {partition}: {e}')
#					else:
#						self.owner.log.info(f'error adding environment partition {partition}: {e}')


#			for controller in environment['controller']:
#				self.owner.log.info ('adding environment controller...')
#				try:
					#hotspare is an option in stack add storage controller, however there is no database column
					#for it in storage_controller and it is not listed in stack list storage controller
					#f'hotspare={controller["hotspare"]}'
#					self.owner.command('add.storage.controller', [ environment_name, f'adapter={controller["adapter"]}', f'arrayid={controller["arrayid"]}', f'enclosure={controller["enclosure"]}', f'raidlevel={controller["raidlevel"]}', f'slot={controller["slot"]}' ])
#				except CommandError as e:
#					if 'exists' in str(e):
#						self.owner.log.info(f'warning adding environment controller {controller}: {e}')
#					else:
#						self.owner.log.info(f'error adding environemnt controller {controller}: {e}')

