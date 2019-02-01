# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'bootaction'

	def run(self, section):

		self.owner.set_scope('global')

		for a in section:
			args   = a.get('name')
			params = {'type'   : a.get('type'),
				  'os'     : a.get('os'),
				  'kernel' : a.get('kernel'),
				  'ramdisk': a.get('ramdisk'),
				  'args'   : a.get('args')}

			self.owner.stack('add.bootaction', args, **params)
