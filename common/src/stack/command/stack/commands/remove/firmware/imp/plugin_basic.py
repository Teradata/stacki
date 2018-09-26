# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import ArgRequired

class Plugin(stack.commands.Plugin):
	"""Attempts to remove implementations."""

	def provides(self):
		return 'basic'

	def run(self, args):
		# Require implementation names
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'imps')
		# remove any duplicates
		args = self.owner.remove_duplicates(args = args)
		# The imps must exist
		self.owner.validate_imps_exist(imps = args)

		# remove the implementations
		self.owner.db.execute('DELETE FROM firmware_imp WHERE name IN %s', (args,))
