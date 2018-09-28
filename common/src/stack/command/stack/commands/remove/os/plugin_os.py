# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'os'

	def requires(self):
		return [ 'TAIL' ]

	def run(self, os):
		self.owner.db.execute('delete from oses where name=%s', (os,))
