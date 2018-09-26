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
	"""Attempts to associate a version_regex with makes."""

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		version_regex, = self.owner.fillParams(
			names = [('version_regex', ''),],
			params = params
		)
		# Require make names
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'makes')

		args = self.owner.remove_duplicates(args = args)
		# The makes must exist
		self.owner.validate_makes_exist(makes = args)
		# A version_regex is required
		if not version_regex:
			raise ParamRequired(cmd = self.owner, param = 'version_regex')
		# The version_regex must exist
		if not self.owner.version_regex_exists(name = version_regex):
			raise ParamError(
				cmd = self.owner,
				param = 'version_regex',
				msg = f'The version_regex {version_regex} does not exist in the database.'
			)

		# get the version_regex ID
		version_regex_id = self.owner.get_version_regex_id(name = version_regex)
		# associate the makes with the version_regex
		self.owner.db.execute('UPDATE firmware_make SET version_regex_id=%s WHERE name in %s', (version_regex_id, args))
