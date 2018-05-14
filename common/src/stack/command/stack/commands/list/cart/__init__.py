# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.CartArgumentProcessor,
	stack.commands.list.command):
	"""
	List the status of available carts.
	
	<arg optional='1' type='string' name='cart' repeat='1'>
	List of carts. This should be the cart base name (e.g., stacki, os,
	etc.). If no carts are listed, then status for all the carts are
	listed.
	</arg>

	<example cmd='list cart kernel'>		
	List the status of the kernel cart.
	</example>
	
	<example cmd='list cart'>
	List the status of all the available carts.
	</example>
	"""		

	def run(self, params, args):
		self.beginOutput()

		for cart in self.getCartNames(args):
		    
			# For each cart determine if it is enabled
			# in any box.
			
			boxes = []

			for row in self.db.select("""b.name from
				cart_stacks s, carts c, boxes b where
				c.name='%s' and
				s.cart=c.id and s.box=b.id """
				% cart):

				boxes.append(row[0])
			
			self.addOutput(cart, ' '.join(boxes))

		self.endOutput(header=['name', 'boxes'], trimOwner=False)

