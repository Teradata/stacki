# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.commands
import json
import yaml
from jsoncomment import JsonComment
import sys
import os
from stack.exception import CommandError, ArgRequired, ArgUnique
import subprocess
import logging
import stack.commands
from stack.bool import str2bool
import re
import shlex


class command(stack.commands.Command):
	MustBeRoot = 0

	def get_scope(self):
		try:
			scope = self.__dump_scope
		except AttributeError:
			scope = 'global'
		return scope

		
	def set_scope(self, scope):
		self.__dump_scope = scope


	def stack(self, cmd, *args, **params):
		if not args or args == (None,):
			args = []
		if not params:
			params = {}
		for key in [key for key in params if params[key] is None]:
			del params[key]	  # nuke *=None params
		c = ' '.join(cmd.split('.'))
		a = ''
		if args:
			a = shlex.quote(' '.join(args))
		p = ' '.join([f'{k}={shlex.quote(str(v))}' for k, v in params.items()])
		print(f'/opt/stack/bin/stack "{c}" {a} {p}')


	def check_required(self, data, section, keys):
		for key in keys:
			if data.get(key) is None:
				raise CommandError(self,
						   f'{section} section missing "{key}"')

			
	def load_file(self, filename):
		scope = self.get_scope()

		_, ext = os.path.splitext(filename)
		if ext.lower() == 'json':
			with open(filename, 'r') as fin:
				data = fin.read()

			parser = JsonComment(json) # standard JSON is stupid
			try:
				document = parser.loads(data)
			except ValueError as e:
				raise CommandError(self, f'syntax error\n{e}')

		else: # yaml
			with open(filename, 'r') as fin:
				try:
					document = yaml.load(fin)
				except yaml.YAMLError as e:
					raise CommandError(self, f'syntax error\n{e}')

		if scope == 'global':
			return document
		return document.get(scope)
			

	def load_access(self, access):
		if not access:
			return

		for a in access:
			params = {'command': a.get('command'),
				  'group'  : a.get('group')}

			self.stack('set.access', None, **params)


	def load_attr(self, attrs, target=None):
		if not attrs:
			return

		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		for a in attrs:
			((key, value), ) = a.items()
			if key == 'shadow' and type(value) == list:
				for a in value:
					((key, value), ) = a.items()
					params = {'scope' : scope,
						  'attr'  : key,
						  'value' : value,
						  'shadow': True}
			else:
				params = {'scope' : scope,
					  'attr'  : key,
					  'value' : value}

			self.stack('set.attr', target, **params)

			
	def load_controller(self, controllers, target=None):
		if not controllers:
			return
		
		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		for c in controllers:
			params = {'enclosure': c.get('enclosure'),
				  'adapter'  : c.get('adapter'),
				  'slot'     : c.get('slot'),
				  'raidlevel': c.get('raidlevel'),
				  'arrayid'  : c.get('arrayid'),
				  'options'  : c.get('options')}

			self.stack('add.storage.controller', target, **params)


	def load_partition(self, partitions, target=None):
		if not partitions:
			return
		
		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		for p in partitions:
			params = {'device'    : p.get('device'),
				  'partid'    : p.get('partid'),
				  'mountpoint': p.get('mountpoint'),
				  'size'      : p.get('size'),
				  'fstype'    : p.get('fstype'),
				  'options'   : p.get('options')}

			self.stack('add.storage.partition', target, **params)


	def load_firewall(self, firewalls, target=None):
		if not firewalls:
			return
		
		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		for f in firewalls:
			params = {'scope'         : scope,
				  'service'       : f.get('service'),
				  'network'       : f.get('network'),
				  'output_network': f.get('output-network'),
				  'chain'         : f.get('chain'),
				  'action'        : f.get('action'),
				  'protocol'      : f.get('protocol'),
				  'flags'         : f.get('flags'),
				  'comment'       : f.get('comment'),
				  'table'         : f.get('table'),
				  'name'          : f.get('name')}
				
			self.stack('add.firewall', target, **params)


	def load_route(self, routes, target=None):
		if not routes:
			return
		
		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		for r in routes:
			params = {'scope'    : scope,
				  'address'  : r.get('address'),
				  'gateway'  : r.get('gateway'),
				  'gateway'  : r.get('subnet'),
				  'netmask'  : r.get('netmask'),
				  'interface': r.get('interface')}

			self.stack('add.route', target, **params)

			
	def run(self, params, args):

		(document, ) = self.fillParams([
			('document', None)
		])

		if not document:
			if not args:
				raise ArgRequired(self, 'filename')
			if len(args) > 1:
				raise ArgUnique(self, 'filename')
		
		filename = args[0]
		_, ext = os.path.splitext(filename)
		if ext.lower() not in [ '.json', '.yaml', '.yml' ]:
			raise CommandError(self, 'invalid file format')

		try:
			document = self.load_file(filename)
		except IOError:
			raise CommandError(self, f'cannot read {filename}')

		self.main(document)



			
class Command(command):
	"""
	Load configuration data from the provided json document. If no arguments
	are provided then all plugins will be run.
	"""

	def main(self, document):

		self.set_scope('global')

		self.load_access(document.get('access'))
		self.load_attr(document.get('attr'))
		self.load_controller(document.get('controller'))
		self.load_partition(document.get('partition'))
		self.load_firewall(document.get('firewall'))

		for plugin in self.loadPlugins():
			section = document.get(plugin.provides())
			if section:
				plugin.run(section)

		
