# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from collections import OrderedDict
import stack.commands
import json
import yaml


class command(stack.commands.Command):


	def get_scope(self):
		scope = self.__dump_scope
		if not scope:
			scope = 'global'
		return scope

		
	def set_scope(self, scope):
		self.__dump_scope = scope


	def dump_attr(self, name=None):
		dump  = []
		scope = self.get_scope()

		if scope == 'global':
			arg = []
		else:
			arg = [name]

		shadow = []
		for row in self.call('list.attr', [f'scope={scope}',
						   'resolve=false',
						   'const=false'] + arg):
			name  = row['attr']
			value = row['value']

			if name not in ['Kickstart_PrivateHostname',
					'Kickstart_PrivateDNSDomain',
					'Info_FQDN',
					'Kickstart_PrivateAddress',
					'Kickstart_PrivateNetwork',
					'Kickstart_PrivateNetmask',
					'Kickstart_PrivateNetmaskCIDR',
					'Kickstart_PrivateBroadcast',
					'Kickstart_PrivateKickstartHost',
					'Kickstart_PrivateNTPHost',
					'Kickstart_PrivateGateway',
					'Kickstart_PrivateDNSServers',
					'Kickstart_PrivateRootPassword' ]:
				continue

			if value.lower() == 'true':
				value = True
			elif value.lower() == 'false':
				value = False
			if row['type'] == 'var':
				dump.append({ name : value })
			else:
				shadow.append({ name : value })

		if shadow:
			dump.append({ 'shadow': shadow })
		
		return dump


	def dump_firewall(self, name=None):
		dump  = []
		scope = self.get_scope()

		arg = [name]
		if scope == 'global':
			arg    = []
			source = 'G'
		elif scope == 'environment':
			source = 'E'
		elif scope == 'os':
			source = 'O'
		elif scope == 'appliance':
			source = 'A'
		elif scope == 'host':
			source = 'H'
		else:
			assert(False) # barf
			
		for row in self.call('list.firewall', [f'scope={scope}'] + arg):
			if row['type'] != 'var' or row['source'] != source:
				continue
			dump.append(OrderedDict(
				service        = row['service'],
				network        = row['network'],
				output_network = row['output-network'],
				chain          = row['chain'],
				action         = row['action'],
				protocol       = row['protocol'],
				flags          = row['flags'],
				comment        = row['comment'],
				table          = row['table'],
				name           = row['name']))
		return dump

	def dump_route(self, name=None):
		dump  = []
		scope = self.get_scope()

		if scope == 'global':
			data = self.call('list.route')
		else:
			data = self.call(f'list.{scope}.route', [name])

		if scope == 'host':
			check_source = lambda row: row['source'] == 'H'
		else:
			check_source = lambda row: True

		for row in data:
			if not check_source(row):
				continue
			dump.append(OrderedDict(
				address   = row['network'],
				gateway   = row['gateway'],
				netmask   = row['netmask']))
		return dump


	def dump_controller(self, name=None):
		dump  = []
		scope = self.get_scope()

		if scope == 'global':
			data = self.call('list.storage.controller')
		else:
			data = self.call('list.storage.controller', [name])

		for row in data:
			dump.append(OrderedDict(
				enclosure = row['enclosure'],
				adapter   = row['adapter'],
				slot      = row['slot'],
				raidlevel = row['raidlevel'],
				arrayid   = row['arrayid'],
				options   = row['options']))
		return dump


	def dump_partition(self, name=None):
		dump  = []
		scope = self.get_scope()

		if scope == 'global':
			data = self.call('list.storage.partition')
		else:
			data = self.call('list.storage.partition', [name])

		for row in data:
			dump.append(OrderedDict(
				device     = row['device'],
				partid     = row['partid'],
				mountpoint = row['mountpoint'],
				size       = row['size'],
				fstype     = row['fstype'],
				options    = row['options']))
		return dump


	def dumps(self, dump):

		def dict_repr(dumper, dump):
			return dumper.represent_dict(dump.items())

		(format, ) = self.fillParams([('format', 'json')], self._params)
					      
		if format == 'json':
			return json.dumps(dump, indent=8)
		elif format == 'yaml':
			dumper = yaml.Dumper
			dumper.add_representer(OrderedDict, dict_repr)
			return yaml.dump(dump, Dumper=dumper, 
					 default_flow_style=False)
		else:
			return dump
			




class Command(command):
	"""
	Dumps the entire state of the Stacki database as a JSON document.
	"""
	def run(self, params, args):
		dump = {}
		
#		params['format'] = 'yaml'

		self.set_scope('global')


		dump = OrderedDict(version    = stack.version,
				   attr       = self.dump_attr())
#				   controller = self.dump_controller(),
#				   partition  = self.dump_partition(),
#				   firewall   = self.dump_firewall(),
#				   route      = self.dump_route())


		for (name, doc) in self.runPlugins():
			if doc:
				if name in [ 'network', 'host' ]:
					dump.update(json.loads(doc))
		
		self.addText(self.dumps(dump))

