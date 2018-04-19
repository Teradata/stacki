# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class command(stack.commands.HostArgumentProcessor,
	stack.commands.list.command):
	pass
	

class Command(command):
	"""
	List the components

	<example cmd='list component'>
	List info for all the known components
	</example>

	"""
	def run(self, params, args):
	    
		(order, ) = self.fillParams([ ('order', 'asc') ])
		
		components = self.getComponentNames(args, order=order)

		values = { }
		for row in self.db.select(
			"""
			c.name, c.type, 
			c.rack, c.rank, c.make, c.model, 
			a.name, e.name, c.comment from
			components c
			left join appliances a   on c.appliance   = a.id
			left join environments e on c.environment = e.id 
			"""):
			values[row[0]] = row[1:]


		self.beginOutput()
		for component in components:
			self.addOutput(component, values[component])
			
		self.endOutput(header = [ 'name', 'type',
					  'rack', 'rank', 'make', 'model', 
					  'appliance', 'environment', 'comment' ], trimOwner=False)
