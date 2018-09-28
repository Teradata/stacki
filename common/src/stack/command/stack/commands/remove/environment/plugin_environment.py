# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):
	def provides(self):
		return 'environment'

	def requires(self):
		# We gotta run last
		return [ 'TAIL' ]

	def run(self, environment):
		self.owner.db.execute(
			'delete from environments where name=%s',
			(environment,)
		)
