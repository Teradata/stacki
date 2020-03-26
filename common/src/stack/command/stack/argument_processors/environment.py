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

from collections import OrderedDict

from stack.exception import ArgNotFound
from stack.util import flatten

class EnvironmentArgProcessor:
	"""
	An Interface class to add the ability to process environment arguments.
	"""

	def getEnvironmentNames(self, args=None):
		environments = []
		if not args:
			args = ['%']		# find everything in table

		for arg in args:
			names = flatten(self.db.select(
				'name from environments where name like %s', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'environment')

			environments.extend(names)

		return sorted(OrderedDict.fromkeys(environments))
