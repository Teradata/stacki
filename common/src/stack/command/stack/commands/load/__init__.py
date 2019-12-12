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
from contextlib import suppress


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

	def _exec_commands(self, cmd, args, params):
		"""Helper to actually run the commands with the self.call machinery."""
		assert self.exec_commands

		call_args = []
		call_args.extend(args)
		call_args.extend(f"{key}={value}" for key, value in params.items())

		# Suppress errors to mimic normal use case of piping through bash without -e.
		# This is because some commands are expected to fail, but the failure doesn't matter.
		# For example: trying to re-add the frontend host on a freshly installed frontend.
		with suppress(CommandError):
			self.call(command = cmd, args = call_args)

	def stack(self, cmd, *args, **params):
		if not args or args == (None,):
			args = tuple()
		if not params:
			params = {}

		# nuke *=None params
		params = {key: value for key, value in params.items() if value is not None}

		# If they actually want us to run the commands, go ahead and run them.
		if self.exec_commands:
			self._exec_commands(cmd = cmd, args = args, params = params)
			return

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
		"""Loads attr information provided into the current scope."""
		if not attrs:
			return

		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		cmd = f'set.{scope}.attr' if scope != 'global' else 'set.attr'

		for attr in attrs:
			params = {
				'attr': attr.get('name'),
				'value': attr.get('value'),
				'shadow': attr.get('shadow'),
			}

			self.stack(cmd, target, **params)


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

	def _validate_raid_device(self, device, partitions_list, raid_devices):
		"""Validate software raid is set up correctly."""
		for partition in partitions_list:
			# Gotta have options
			if not partition.get('options'):
				raise CommandError(
					self,
					f'missing options for software raid device "{device}"'
				)

			# First part of options needs to define the RAID level
			parts = partition['options'].split()
			if not parts[0].startswith("--level=RAID"):
				raise CommandError(
					self,
					f'missing "--level=RAID" option for software raid device "{device}"'
				)

			# The other parts need to be valid RAID devices
			for part in parts[1:]:
				if part not in raid_devices:
					raise CommandError(
						self,
						f'device "{part}" not defined for software raid device "{device}"'
					)

	def _validate_lvm_partition(self, partitions_list):
		"""Make sure that LVM partitions have names."""
		for partition in partitions_list:
			options = partition.get('options')
			if not options or "--name=" not in options:
				raise CommandError(
					self,
					f'missing "--name" option for LVM partition "{partition["mountpoint"]}"'
				)

	def validate_partition(self, partitions):
		"""Validates that the partitions provided are valid as a whole."""
		# Now that we've processed the spreadsheet, do some sanity checks
		md_regex = re.compile(r'md[0-9]+')
		hd_regex = re.compile(r'xvd[a-z]+|[shv]d[a-z]+|nvme[0-9]+n[0-9]+')

		# Construct some lookup tables based on mount point
		raid_devices = set()
		lvm_devices = set()
		volgroup_devices = set()

		# map partitions by device for validation
		devices = {
			partition.get("device"): []
			for partition in partitions
		}
		for partition in partitions:
			devices[partition.get("device")].append(partition)

		for partitions_list in devices.values():
			for partition in partitions_list:
				if partition.get('fstype') == 'raid':
					raid_devices.add(partition['mountpoint'])
				elif partition.get('fstype') == 'lvm':
					lvm_devices.add(partition['mountpoint'])
				elif partition.get('fstype') == 'volgroup':
					volgroup_devices.add(partition['mountpoint'])

		# Check the devices for this target
		valid_devices = set()
		for device, partitions_list in devices.items():
			# Make sure software raid devices have valid options
			if md_regex.fullmatch(device):
				self._validate_raid_device(
					device = device,
					partitions_list = partitions_list,
					raid_devices = raid_devices,
				)
				valid_devices.add(device)

			# Physical devices are valid
			elif hd_regex.fullmatch(device):
				valid_devices.add(device)

			# Partitions inside an LVM volume groups need names
			elif device in volgroup_devices:
				self._validate_lvm_partition(partitions_list = partitions_list)
				valid_devices.add(device)

			else:
				# LVM volume groups need LVM devices
				volgroups = [
					partition for partition in partitions_list
					if partition['fstype'] == 'volgroup'
				]
				if volgroups:
					if device not in lvm_devices:
						raise CommandError(
							self,
							f'device "{device}" not defined for volgroups: {", ".join(volgroup["mountpoint"] for volgroup in volgroups)}'
						)

					valid_devices.add(device)

		# Make sure all the devices for this host have been validated
		unknown_devices = set(devices.keys()).difference(valid_devices)
		if unknown_devices:
			raise CommandError(self, f"unknown device(s) detected: {', '.join(unknown_devices)}")

	def load_partition(self, partitions, target=None):
		"""Loads partition information provided into the current scope."""
		if not partitions:
			return

		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		# Validate partitions if not being forced.
		if not self.force:
			self.validate_partition(partitions = partitions)

		# Remove all existing entries based on which scope we are operating in.
		self.stack(
			f'remove.{scope}.storage.partition' if scope != 'global' else 'remove.storage.partition',
			target,
			device='*',
		)

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
		"""Loads firewall information provided into the current scope."""
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
		"""Loads route information provided into the current scope."""
		if not routes:
			return

		scope = self.get_scope()
		assert not (scope != 'global' and target is None)

		cmd = f'add.{scope}.route' if scope != 'global' else 'add.route'

		for route in routes:
			# In `add route` the gateway parameter is overloaded to either be a subnet(network) name or a gateway.
			# We need to chose whichever one is set in the dump.
			gateway = route.get('gateway')
			params = {
				'address': route.get('address'),
				# Specifically not using `is not None` because we also want to reject the empty string.
				'gateway': gateway if gateway else route.get('subnet'),
				'netmask': route.get('netmask'),
				'interface': route.get('interface'),
			}

			self.stack(cmd, target, **params)


	def run(self, params, args):

		document, self.exec_commands, self.force = self.fillParams([
			('document', None),
			('exec', False),
			('force', False),
		])
		self.exec_commands = str2bool(self.exec_commands)
		self.force = str2bool(self.force)

		if not document:
			if not args:
				raise ArgRequired(self, 'filename')
			if len(args) > 1:
				raise ArgUnique(self, 'filename')

			document = args[0]

		document = self.load_file(document)

		self.main(document)




class Command(command):
	"""
	Load configuration data from the provided JSON document.

	A series of stack commands will be printed to STDOUT which, if run, would
	import the data in the JSON document into the stacki database.  Note, all of
	these commands are database manipulation - commands such as 'sync config',
	'sync host network', 'sync host boot', etc. must be run manually.

	<example cmd='stack load dump.json | bash'>
	The data in 'dump.json' will be converted into stack commands and run.
	</example>

	<param type='string' name='document'>
	A JSON document to parse.  If omitted, will attempt to use the first argument
	</param>

	<param type='boolean' name='exec'>
	If set to True, load commands will be automatically executed and output suppressed.
	This is much faster than piping through bash.  Defaults to False.
	</param>

	<param type='boolean' name='force'>
	If set to True, will disregard any non-syntax validation done on the json data.
	This is useful to, for example, load incomplete partitioning data, which the admin
	intends to complete later..
	Defaults to False.
	</param>

	<related>dump</related>
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
