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

class OSArgumentProcessor:
	"""
	An Interface class to add the ability to process os arguments.
	"""

	def getOSNames(self, args=None):
		oses = []
		if not args:
			args = ['%']		# find everything in table

		for arg in args:
			if arg == 'centos':
				if 'redhat' in oses:
					continue
				arg = 'redhat'

			names = flatten(self.db.select(
				'name from oses where name like %s order by name', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'OS')

			oses.extend(names)

		return sorted(OrderedDict.fromkeys(oses))
