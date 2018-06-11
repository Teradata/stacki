# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'basic'

	def run(self, hosts):
		host_info = dict.fromkeys(hosts)

		for row in self.db.select(
		"""
                n.name, rack, rank, a.name
                from nodes n, appliances a
                where n.appliance = a.id
                and a.name = 'switch'
                """):

			if row[0] in host_info:
				host_info[row[0]] = row[1:]
				host_info[row[0]] += tuple([self.owner.getHostAttr(row[0], 'component.model')])

		for host in dict(host_info):
			if host_info[host] == None:
				del host_info[host]
	
		return { 'keys' : [ 'rack',
				    'rank',
				    'appliance',
				    'model',
				    ],
			'values': host_info }


