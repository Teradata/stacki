# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'network'

	def run(self, section):

		self.owner.set_scope('global')

		for n in section:
			args   = n.get('name')
			params = {'address': n.get('address'),
				  'mask'   : n.get('mask'),
				  'gateway': n.get('gateway'),
				  'mtu'    : n.get('mtu'),
				  'zone'   : n.get('zone'),
				  'dns'    : n.get('dns'),
				  'pxe'    : n.get('pxe')}
			
			self.owner.stack('add.network', args, **params)

