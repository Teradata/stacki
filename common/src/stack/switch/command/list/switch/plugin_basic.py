# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'basic'

	def run(self, hosts):
		host_info = dict.fromkeys(hosts)

		stmt = """
		n.name, rack, rank, a.name
		FROM nodes n, appliances a
		WHERE n.appliance = a.id
		AND a.name = 'switch'
		"""

		for row in self.db.select(stmt):
			sw_name = row[0]
			if sw_name in host_info:
				host_info[sw_name] = (*row[1:],
							self.owner.getHostAttr(sw_name, 'component.make'),
							self.owner.getHostAttr(sw_name, 'component.model'))

		for host in dict(host_info):
			if host_info[host] == None:
				del host_info[host]
	
		return { 'keys' : [ 'rack',
				    'rank',
				    'appliance',
				    'make',
				    'model',
				    ],
			'values': host_info }


