# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.bool import str2bool
import stack.commands
from stack.commands import HostArgProcessor, SwitchArgProcessor
from stack.exception import ArgUnique, CommandError
from stack.switch.m7800 import SwitchMellanoxM7800


class Command(HostArgProcessor, SwitchArgProcessor, stack.commands.set.command):
	"""
	Enable the subnet manager for the given switch.

	<arg type='string' name='switch'>
	Exactly one infiniband switch name which will become the subnet manager for
	the fabric it is on.  All other infiniband switches on the same fabric will
	have their subnet manager status disabled.  Fabric is determined soley based
	on the 'ibfabric' attribute.
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
			'username': self.switch_attrs[hostname].get('switch_username'),
			'password': self.switch_attrs[hostname].get('switch_password'),
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

		self.switch_attrs = self.getHostAttrDict(ib_switch_names)

		if self.switch_attrs[sm_switch].get('switch_type') != 'infiniband':
			msg = f'{sm_switch} is not an infiniband switch, please verify "stack list host attr {sm_switch} attr=switch_type"'

		if disable:
			# explicit disable only affects this switch
			switch = self.get_sw_handle(sm_switch)
			switch.subnet_manager = False
			switch.disconnect()
			return

		# NOTE assumes a single management port with options set.
		# this obviously breaks if a switch can someday be on multiple fabrics
		fabric = self.switch_attrs[sm_switch].get('ibfabric')
		if not fabric:
			raise CommandError(self, f'switch {sm_switch} does not have its ibfabric set')

		switches_to_disable = []
		for ib_sw in ib_switch_names:
			if ib_sw == sm_switch:
				# this one is the sm
				continue

			sw_fabric = self.switch_attrs[ib_sw].get('ibfabric')
			if not sw_fabric or sw_fabric == fabric:
				# switches with no fabric specified should be disabled
				# other switches on the same fabric should be disabled
				switches_to_disable.append(ib_sw)
				continue

		for switch in switches_to_disable:
			sw_handle = self.get_sw_handle(switch)
			sw_handle.subnet_manager = False
			sw_handle.disconnect()

		sw_handle = self.get_sw_handle(sm_switch)
		sw_handle.subnet_manager = True
		sw_handle.disconnect()
