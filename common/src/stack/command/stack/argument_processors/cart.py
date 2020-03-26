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

from stack.exception import ArgNotFound
from stack.util import flatten

class CartArgProcessor:
	"""
	An Interface class to add the ability to process cart arguments.
	"""

	def getCartNames(self, args):
		carts = []
		if not args:
			args = ['%']		 # find all cart names

		for arg in args:
			names = flatten(self.db.select(
				'name from carts where name like binary %s', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'cart')

			carts.extend(names)

		return carts
