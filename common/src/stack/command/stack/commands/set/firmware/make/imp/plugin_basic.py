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
from stack.exception import ArgRequired, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to associate an implementation with makes."""

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		imp, = self.owner.fillParams(
			names = [('imp', ''),],
			params = params
		)
		# Require make names
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'makes')

		args = self.owner.remove_duplicates(args = args)
		# The makes must exist
		self.owner.validate_makes_exist(makes = args)
		# A implementation is required
		if not imp:
			raise ParamRequired(cmd = self.owner, param = 'imp')
		# The implementation must exist
		if not self.owner.imp_exists(imp = imp):
			raise ParamError(
				cmd = self.owner,
				param = 'imp',
				msg = f'The implementation {imp} does not exist in the database.'
			)

		# get the implementation ID
		imp_id = self.owner.get_imp_id(imp_name = imp)
		# associate the makes with the imp
		self.owner.db.execute('UPDATE firmware_make SET imp_id=%s WHERE name in %s', (imp_id, args))
