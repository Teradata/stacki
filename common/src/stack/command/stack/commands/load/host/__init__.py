# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
from stack.exception import CommandError, ArgRequired, ArgUnique
import stack.commands


class Command(stack.commands.load.command):



	def check_host(self, host):
		self.check_required(host, 'host', ('name', 'appliance', 'rack', 'rank'))


	def check_interface(self, interfaces):
		for interface in interfaces:
			self.check_required(interface, 'interface',
					    ('interface', 'mac', 'ip', 'network'))


	def load_interface(self, interfaces, host):
		for interface in interfaces:
			name   = interface['interface']
			params = {}
			for param, field in [('interface', 'interface'),
					     ('mac',       'mac'),
					     ('ip',        'ip'),
					     ('network',   'network'),
					     ('name',      'name'),
					     ('default',   'default'),
					     ('module',    'module'),
					     ('vlan',      'vlan'),
					     ('options',   'options'),
					     ('channel',   'channel')]:
				value = interface.get(field)
				if value:
					params[param] = value
			self.stack('add.host.interface', name, **params)
			
			for alias in interface.get('alias'):
				self.stack('add.host.alias', name, 
					   {'alias': alias},
					   {'interface': interface['interface']})

		
	def load_host(self, host):
		name = host['name']

		params = {'appliance': host['appliance'],
			  'rack'     : host['rack'],
			  'rank'     : host['rank'] }

		for key in [ 'box', 'environment', 
			     'osaction', 'installaction', 
			     'comment', 'metadata' ]:
			val = host.get(key)
			if val:
				params[key] = val
				
		self.stack('add.host', name, **params)

	def run(self, params, args):

		if not args:
			raise ArgRequired(self, 'filename')
		if len(args) > 1:
			raise ArgUnique(self, 'filename')

		control = (('interface', self.check_interface, self.load_interface),
			   ('attr',      self.check_attr,      self.load_attr))

		self.set_scope('host')

		document = self.load_file(args[0])

		for section in document:
			self.check_host(section)
			for key, fn, _ in control:
				fn(section[key])

		for section in document:
			hostname = section['name']
			self.load_host(section)
			for key, _, fn in control:
				fn(section[key], hostname)




