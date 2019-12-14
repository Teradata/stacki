# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.kvm import Hypervisor, VmException
from stack.exception import ArgError

class Command(stack.commands.list.vm.storage.Command):
	"""
	List the storage pool information on a hypervisor

	<arg optional='1' type='string' name='hypervisor' repeat='1'>
	The hypervisor to list storage pool info from.
	</arg>

	<param type='string' name='pool'>
	Only show pool info for a pool with the
	specified name.
	</param>

	<example cmd='list vm pool hypervisor-0-0'>
	List hypervisor-0-0 storage information.
	</example>

	<example cmd='list vm storage pool hypervisor-0-0'>
	List all storage pool information on hypervisor-0-0
	</example>

	<example cmd='list vm storage pool hypervisor-0-0 pool=stacki'>
	Only list storage pool information for pool stacki on
	hypervisor-0-0
	</example>
	"""

	def run(self, param, args):
		pool, = self.fillParams([
			('pool', '')
		])
		if not args:
			return
		for arg in args:
			if not self.is_hypervisor(arg):
				raise ArgError(self, 'hypervisor', f'{arg} is not a valid hypervisor')

		self.beginOutput()
		header = [
			'Host',
			'Name',
			'Allocated',
			'Available',
			'Capacity',
			'Pool Active'
		]
		for arg in args:
			conn = Hypervisor(arg)
			pool_info = conn.pool_info(filter_pool=pool)
			for pool, values in pool_info.items():
				pool_values = [
						pool,
						values['allocated'],
						values['available'],
						values['capacity'],
						values['is_active']
					]
				self.addOutput(owner = arg, vals = pool_values)
		self.endOutput(header=header, trimOwner=False)
