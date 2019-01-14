# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import re
import stack.commands
from stack.exception import ArgRequired, ArgUnique, ParamRequired, ParamError

class Plugin(stack.commands.Plugin):
	"""Attempts to add all provided make names to the database."""

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		name, = self.owner.fillParams(
			names = [('name', ''),],
			params = params
		)
		# Require a version regex
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'regex')
		# Should only be one
		if len(args) != 1:
			raise ArgUnique(cmd = self.owner, arg = 'regex')
		# A name is required
		if not name:
			raise ParamRequired(cmd = self.owner, param = 'name')
		# Require the version_regex to be a valid regex
		version_regex = args[0]
		try:
			re.compile(version_regex)
		except re.error as ex:
			raise ParamError(
				cmd = self.owner,
				param = 'version_regex',
				msg = f'Invalid regex supplied: {ex}.'
			)

		self.owner.db.execute(
			'''
			INSERT INTO firmware_version_regex (
				regex,
				name
			)
			VALUES (%s, %s)
			''',
			(version_regex, name)
		)
