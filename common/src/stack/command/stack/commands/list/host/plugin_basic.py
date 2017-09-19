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
		dict = {}
		for host in hosts:
			dict[host] = True
			
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
			left join oses o	 on b.os = o.id
			"""):

			if row[0] in dict:
				dict[row[0]] = row[1:]
	
		return { 'keys' : [ 'rack',
				    'rank',
				    'appliance',
				    'os',
				    'box',
				    'environment',
				    'osaction',
				    'installaction' ],
			'values': dict }

