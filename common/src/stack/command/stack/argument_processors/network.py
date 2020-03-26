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

class NetworkArgProcessor:
	"""
	An Interface class to add the ability to process network (subnet) argument.
	"""

	def getNetworkNames(self, args=None):
		"""
		Returns a list of network (subnet) names from the database. For
		each arg in the ARGS list find all the network names that match
		the arg (assume SQL regexp). If an arg does not match anything
		in the database we raise an exception. If the ARGS list is empty
		return all network names.
		"""

		networks = []
		if not args:
			args = [ '%' ]		   # find all networks

		for arg in args:
			names = flatten(self.db.select(
				'name from subnets where name like %s', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'network')

			networks.extend(names)

		return networks

	def getNetworkName(self, netid):
		"""
		Returns a network (subnet) name from the database that
		is associated with the id 'netid'.
		"""

		if not netid:
			return ''

		rows = self.db.select('name from subnets where id=%s', (netid,))

		if rows:
			netname = rows[0][0]
		else:
			netname = ''

		return netname
