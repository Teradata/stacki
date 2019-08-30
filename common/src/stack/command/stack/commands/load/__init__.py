# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.commands
import json
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

	def _load(self, text):
		parser = JsonComment(json) # standard JSON is stupid
		try:
			data = parser.loads(text)
		except ValueError as e:
			# parse the error message and split the input at the
			# syntax error
			i = int(re.search(r'char (.*?)\)', str(e)).group(1))
			b = text[:i]
			a = text[i:]

			# find the line with the error and report it
			# 'blen' in honor of our intern

			line1 = (b[b.rfind('\n'):] + a[:a.find('\n')]).strip()
			blen  = len((b[b.rfind('\n'):]).strip())
			line2 = ' ' * blen + '^'
			raise CommandError(self,
					   f'syntax error\n{line1}\n{line2}\n{e}')
		return data

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

		try:
			fin  = open(filename, 'r')
			data = fin.read()
		except IOError:
			raise CommandError(self, f'cannot read {filename}')
		document = self._load(data)
		if scope == 'global':
			return document
		else:
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
			params = {'scope' : scope,
				  'attr'  : a.get('name'),
				  'value' : a.get('value'),
				  'shadow': a.get('shadow')}

			self.stack('set.attr', target, **params)


	def load_controller(self, controllers, target=None):
		"""Loads controller information provided into the current scope."""
		if not controllers:
			return

		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		cmd = f'add.{scope}.storage.controller' if scope != 'global' else 'add.storage.controller'

		for controller in controllers:
			params = {
				'enclosure': controller.get('enclosure'),
				'adapter': controller.get('adapter'),
				'slot': controller.get('slot'),
				'raidlevel': controller.get('raidlevel'),
				'arrayid': controller.get('arrayid'),
				'options': controller.get('options'),
			}

			self.stack(cmd, target, **params)

	def load_partition(self, partitions, target=None):
		"""Loads partition information provided into the current scope."""
		if not partitions:
			return

		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		cmd = f'add.{scope}.storage.partition' if scope != 'global' else 'add.storage.partition'

		for partition in partitions:
			params = {
				'device': partition.get('device'),
				'partid': partition.get('partid'),
				'mountpoint': partition.get('mountpoint'),
				'size': partition.get('size'),
				'type': partition.get('fstype'),
				'options': partition.get('options'),
			}

			self.stack(cmd, target, **params)


	def load_firewall(self, firewalls, target=None):
		if not firewalls:
			return

		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		cmd = f'add.{scope}.firewall' if scope != 'global' else 'add.firewall'

		for firewall in firewalls:
			params = {
				'service': firewall.get('service'),
				'network': firewall.get('network'),
				'output_network': firewall.get('output-network'),
				'chain': firewall.get('chain'),
				'action': firewall.get('action'),
				'protocol': firewall.get('protocol'),
				'flags': firewall.get('flags'),
				'comment': firewall.get('comment'),
				'table': firewall.get('table'),
				'rulename': firewall.get('name'),
			}

			self.stack(cmd, target, **params)


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
			document = self.load_file(args[0])

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
