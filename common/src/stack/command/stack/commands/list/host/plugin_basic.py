# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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
			hv.name, hv.rack, hv.rank, hv.make, hv.model,
			a.name,
			o.name, b.name, 
			e.name, 
			bno.name, bni.name from 
			host_view hv
			left join appliances a   on hv.appliance     = a.id
			left join boxes b        on hv.box           = b.id 
			left join environments e on hv.environment   = e.id 
			left join bootnames bno  on hv.osaction      = bno.id 
			left join bootnames bni  on hv.installaction = bni.id
			left join oses o	 on b.os = o.id
			"""):

			if row[0] in host_info:
				host_info[row[0]] = row[1:]
	
		return { 'keys' : [ 'rack',
				    'rank',
				    'make',
				    'model',
				    'appliance',
				    'os',
				    'box',
				    'environment',
				    'osaction',
				    'installaction' ],
			'values': host_info }

