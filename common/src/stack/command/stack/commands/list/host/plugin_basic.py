# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'basic'

	def run(self, args):
		(hosts, expanded, hashit) = args

		keys      = [ ] 
		host_info = dict.fromkeys(hosts)
		for host in hosts:
			host_info[host] = []

		if expanded:
			# This is used by the MessageQ as a permanent handle on
			# Redis keys. This allows both the networking and names
			# of hosts to change and keeps the mq happy -- doesn't
			# break the status in 'list host'.
			keys.append('id')
			for name, id in self.db.select('name, id from nodes'):
				if name in host_info:
					host_info[name] = [ id ]

		for row in self.db.select(
			"""
			n.name, n.rack, n.rank, 
			a.name,
			o.name, b.name, 
			e.name, 
			bno.name, bni.name from 
			nodes n 
			left join appliances a   on n.appliance     = a.id
			left join boxes b        on n.box           = b.id 
			left join environments e on n.environment   = e.id 
			left join bootnames bno  on n.osaction      = bno.id 
			left join bootnames bni  on n.installaction = bni.id
			left join oses o	 on b.os            = o.id
			"""):

			if row[0] in host_info:
				host_info[row[0]].extend(row[1:])

		keys.extend(['rack', 'rank',
			     'appliance',
			     'os', 'box',
			     'environment',
			     'osaction', 'installaction'])

		return { 'keys' : keys, 'values': host_info }

