# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import shlex

import stack.commands
from stack.bool import str2bool
from stack.exception import ArgUnique, CommandError
from stack.switch.m7800 import SwitchMellanoxM7800


class Command(stack.commands.SwitchArgumentProcessor,
		stack.commands.HostArgumentProcessor,
		stack.commands.set.command):
	"""
	Enable the subnet manager for the given switch.

	<arg type='string' name='switch'>
	Exactly one infiniband switch name which will become the subnet manager for
	the fabric it is on.  All other infiniband switches on the same fabric will
	have their subnet manager status disabled.
	</arg>

	<param type='boolean' name='disable' optional='1'>
	When set to True, will disable subnet manager status on that switch only.
	Defaults to False.
	</param>

	<example cmd='set switch sm infiniband-3-12'>
	Set the switch infiniband-3-12 to be the only subnet manager for its fabric.
	</example>
	"""

	def get_sw_handle(self, hostname):

		kwargs = {
			'username': self.switch_attrs[hostname].get('username'),
			'password': self.switch_attrs[hostname].get('password'),
		}

		# remove username and pass attrs (aka use any pylib defaults) if they aren't host attrs
		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		s = SwitchMellanoxM7800(hostname, **kwargs)
		s.connect()
		return s


	def run(self, params, args):
		if len(args) != 1:
			raise ArgUnique(self, 'switch')

		sm_switch = args[0]

		(disable, ) = self.fillParams([
			('disable', False),
		])

		disable = str2bool(disable)

		ibswitches = [sw for sw in self.call('list.switch') if sw['model'] == 'm7800']
		ib_switch_names = [sw['switch'] for sw in ibswitches]

		if sm_switch not in ib_switch_names:
			msg = f'host {sm_switch} is not a supported infiniband switch\n'
			msg += 'Please verify the make and model attributes for this host.'
			raise CommandError(self, msg)

		ib_sw_nets = self.call('list.host.interface', ib_switch_names)

		self.switch_attrs = self.getHostAttrDict(ib_switch_names)

		if disable:
			switch = self.get_sw_handle(sm_switch)
			switch.subnet_manager = False
			switch.disconnect()
			return

		# NOTE assumes a single management port with options set.
		# this obviously breaks if a switch can someday be on multiple fabrics

		opts = next(sw['options'] for sw in ib_sw_nets if sw['host'] == sm_switch)
		if not opts:
			raise CommandError(self, f'switch {sm_switch} does not have its ibfabric set')

		for opt in shlex.split(opts):
			if opt.startswith('ibfabric='):
				_, fabric = opt.split('=')
				break

		if not fabric:
			raise CommandError(self, f'switch {sm_switch} does not have its ibfabric set')

		switches_to_disable = []
		for ib_sw in ib_sw_nets:
			if ib_sw['host'] == sm_switch:
				# this is the sm
				continue

			if not ib_sw['options']:
				# switches with no fabric specified should be disabled
				switches_to_disable.append(ib_sw['host'])
				continue

			opts = [opt for opt in shlex.split(ib_sw['options']) if opt.startswith('ibfabric=')]
			if not opts:
				# switches with no fabric specified should be disabled
				switches_to_disable.append(ib_sw['host'])
				continue

			_, sw_fabric = opts[0].split('=')
			if sw_fabric == fabric:
				# other switches on the same fabric should be disabled
				switches_to_disable.append(ib_sw['host'])
				continue

		for switch in switches_to_disable:
			sw_handle = self.get_sw_handle(switch)
			sw_handle.subnet_manager = False
			sw_handle.disconnect()

		sw_handle = self.get_sw_handle(sm_switch)
		sw_handle.subnet_manager = True
		sw_handle.disconnect()
